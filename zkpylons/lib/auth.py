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

from .predicates import Predicate, in_group
from repoze.who.api import get_api
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin, SQLAlchemyUserMDPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
# TODO: repoze.who.plugins.browserid
from repoze.who.classifiers import default_request_classifier, default_challenge_decider
from repoze.who.middleware import PluggableAuthenticationMiddleware

# Import to provide a centralised export point
from .protectors import ActionProtector, ControllerProtector
from .predicates import is_user, in_group, All, Any, Not, not_anonymous

from paste.httpexceptions import HTTPClientError
from webob.exc import HTTPForbidden, HTTPUnauthorized

log = logging.getLogger(__name__)


def add_auth(app,config):

    # Setting the repoze.who authenticators:
    who_args = {}
    who_args['authenticators'] = []
        
    sqlauth = SQLAlchemyAuthenticatorPlugin(Person, meta.Session)
    sqlauth.translations.update({'user_name':'email_address', 'validate_password':'check_password'})
    cookie = AuthTktCookiePlugin('my_secret', 'authtkt',
                                 timeout=None, reissue_time=None)
    # TODO: cookie secret needs to come from somewhere...
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

    who_args['classifier'] = default_request_classifier
    who_args['challenge_decider'] = default_challenge_decider

    # Make testing easier
    #who_args['skip_authentication'] = config.get('skip_authentication')
    
    # TODO: Switch to ini based configuration
    # http://repozewho.readthedocs.org/en/latest/configuration.html#declarative-configuration
    # middleware = setup_auth(app, group_adapters, {}, **who_args)
    middleware = PluggableAuthenticationMiddleware(app, **who_args)
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
    if response.status_int == 401:
        message = 'You are not logged in.'
        message_type = 'warning'
    else:
        message = 'You do not have the permissions to access this page.'
        message_type = 'error'

    #flash(message, message_type) # TODO: import errors (loop)
    #redirect(url('/login', came_from=url.current()))
    abort(response.status_int, comment=reason)

class NotAuthorizedError(HTTPForbidden):
    pass

class ActionProtector(ActionProtector):
    default_denial_handler = staticmethod(redirect_auth_denial)

def has_group(group):
    return in_group(group).is_met(request.environ)

def has_organiser_role():
    return has_group('organiser')

def has_reviewer_role():
    return has_group('reviewer')

def has_funding_reviewer_role():
    return has_group('funding_reviewer')

def has_late_submitter_role():
    return has_group('late_submitter')

def get_person():
    email = request.environ.get('REMOTE_USER')
    return Person.find_by_email(email, abort_404=False) if email is not None else None

def get_person_id():
    person = get_person()
    return person.id if person is not None else None

class is_activated(Predicate):
    message = "Your user account must be activated to continue"
    def evaluate(self, environ, credentials):
        p = get_person()
        if p is None:
            self.unmet()
        if not p.activated:
            # TODO: I don't like the idea of doing redirects in a tester
            #self.unmet(p.activated)
            # TODO: Should I be using zkpylons.lib.helpers.redirect_to()?
            redirect(url(controller="person", action="activate"))


def require_group(group):
    if not in_group(group).is_met(request.environ):
        if not session.get('role_error', None):
            session['role_error'] = "User doesn't have any of the specified roles"
            session.save()
        raise NotAuthorizedError("User doesn't have any of the specified roles")
    else:
        pass

