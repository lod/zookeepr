# Zookeepr driver for AuthKit
#
# This module allows us to use the authkit infrastructure but using the
# Zookeepr models to do so
#  * We don't support groups
#  * We don't support the creation methods as zkpylons does that already
#


import logging

from zkpylons.model import meta, Person, Role
#from zkpylons.lib.helpers import flash

from pylons import request, response, session
from pylons.controllers.util import redirect, abort
from pylons import url

from repoze.what.middleware import setup_auth
from repoze.what.predicates import Predicate, in_group
from repoze.who.api import get_api
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin, SQLAlchemyUserMDPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
# TODO: repoze.who.plugins.browserid
from repoze.what.plugins import pylonshq
from repoze.what.plugins.sql import configure_sql_adapters

# Import to provide a centralised export point
from repoze.what.plugins.pylonshq import ActionProtector
from repoze.what.predicates import is_user, in_group, All, Any, not_anonymous


log = logging.getLogger(__name__)


def add_auth(app,config):

    # Mostly a copy from repoze.what.plugins.quickstart.setup_sql_auth
    source_adapters = configure_sql_adapters(
            Person,
            Role,
            None,
            meta.Session,
            {'item_name' : 'email_address', 'items':'people', 'section_name':'name', 'sections':'roles'},
            {})

    group_adapters= {}
    group_adapter = source_adapters.get('group')
    if group_adapter:
        group_adapters = {'sql_auth': group_adapter}

    permission_adapters = {}
    
    # Setting the repoze.who authenticators:
    who_args = {}
    who_args['authenticators'] = []
        
    sqlauth = SQLAlchemyAuthenticatorPlugin(Person, meta.Session)
    sqlauth.translations.update({'user_name':'email_address', 'validate_password':'check_password'})
    cookie = AuthTktCookiePlugin('my_secret', 'authtkt',
                                 timeout=None, reissue_time=None)
    who_args['authenticators'].append(('sqlauth', sqlauth))
    who_args['authenticators'].append(('auth_tkt', cookie))
    

    # form fields: login, password
    form = FriendlyFormPlugin(
        login_form_url      = '/person/signin',
        login_handler_path  = '/person/do_signin',
        post_login_url      = '/person/post_signin', # Redirected regardless of login success
        logout_handler_path = '/person/signout',
        post_logout_url     = '/',
        login_counter_name  = None,
        rememberer_name     = 'cookie',
        charset             = None,
        )
    
    # Setting the repoze.who identifiers
    who_args['identifiers'] = []
    who_args['identifiers'].append(('cookie', cookie))
    who_args['identifiers'].insert(0, ('main_identifier', form))
    
    # Setting the repoze.who challengers:
    who_args['challengers'] = []
    who_args['challengers'].append(('form', form))
    
    # Setting up the repoze.who mdproviders:
    sql_user_md = SQLAlchemyUserMDPlugin(Person, meta.Session)
    sql_user_md.translations.update({'user_name':'email_address'})
    who_args['mdproviders'] = []
    who_args['mdproviders'].append(('sql_user_md', sql_user_md))

    who_args['log_stream'] = log
    who_args['log_level'] = logging.DEBUG
    
    middleware = setup_auth(app, group_adapters, {}, **who_args)
    return middleware

def override_login(email):
    """ Force a login with the supplied credentials.
        This is useful for automatic login, on account creation or password reset.
    """

    # Set up identity environment for repoze
    cookie = AuthTktCookiePlugin('my_secret', 'authtkt',
                                 timeout=None, reissue_time=None)
    request.environ['repoze.who.identity'] = {
        'identifier': cookie,
        'repoze.who.userid': email,
    }
    get_api(request.environ).remember()


def redirect_auth_denial(reason):
    print "REDIRECT-AUTH-DENIAL", reason, request, response

    if response.status_int == 401:
        message = 'You are not logged in.'
        message_type = 'warning'
    else:
        message = 'You do not have the permissions to access this page.'
        message_type = 'error'

    #flash(message, message_type) # TODO: import errors (loop)
    #redirect(url('/login', came_from=url.current()))
    abort(response.status_int, comment=reason)

class ActionProtector(pylonshq.ActionProtector):
    default_denial_handler = staticmethod(redirect_auth_denial)

def has_organiser_role():
    return in_group('organiser').is_met(request.environ)

def has_reviewer_role():
    return in_group('reviewer').is_met(request.environ)

def has_funding_reviewer_role():
    return in_group('funding_reviewer').is_met(request.environ)

def has_late_submitter_role():
    return in_group('late_submitter').is_met(request.environ)

def get_person_id():
    return Person.find_by_email(request.environ['REMOTE_USER']).id

class is_activated(Predicate):
    message = "Your user account must be activated to continue"
    def evaluate(self, environ, credentials):
        print "CREDS", credentials
        p = Person.find_by_email(environ['REMOTE_USER']);
        if not p.activated:
            # TODO: I don't like the idea of doing redirects in a tester
            #self.unmet(p.activated)
            # TODO: Should I be using zkpylons.lib.helpers.redirect_to()?
            redirect(url(controller="person", action="activate"))
