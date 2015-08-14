# Zookeepr driver for AuthKit
#
# This module allows us to use the authkit infrastructure but using the
# Zookeepr models to do so
#  * We don't support groups
#  * We don't support the creation methods as zkpylons does that already
#


import logging

from pylons.templating import render_mako as render
from pylons import tmpl_context as c
from pylons import request

from formencode import validators, htmlfill, Invalid
from zkpylons.lib.validators import BaseSchema

from zkpylons.model import meta
from zkpylons.model import Person, Role, Proposal, Invoice, Registration, Funding, URLHash

from authkit import users
from authkit.permissions import HasAuthKitRole, UserIn, NotAuthenticatedError, NotAuthorizedError, Permission, PermissionError
from authkit.authorize import PermissionSetupError, middleware
from authkit.authorize.pylons_adaptors import authorized

from pylons import request, response, session
from pylons.controllers.util import redirect, abort
from pylons import url

#import zkpylons.lib.helpers as h

from repoze.what.plugins.quickstart import setup_sql_auth
from repoze.what.plugins import pylonshq
from repoze.what.middleware import setup_auth
from repoze.what.plugins.sql import configure_sql_adapters
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin, SQLAlchemyUserMDPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin

import hashlib

log = logging.getLogger(__name__)



from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.redirector import RedirectorPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin
from StringIO import StringIO
import sys

def basic_add_auth(app, config):
    io = StringIO()
    salt = 'aa'
    for name, password in [ ('admin', 'admin'), ('chris', 'chris') ]:
        io.write('%s:%s\n' % (name, password))
    io.seek(0)
    def cleartext_check(password, hashed):
        return password == hashed
    htpasswd = HTPasswdPlugin(io, cleartext_check)
    basicauth = BasicAuthPlugin('repoze.who')
    auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt')
    redirector = RedirectorPlugin('/login')
    redirector.classifications = {IChallenger:['browser'],} # only for browser
    identifiers = [('auth_tkt', auth_tkt),
                ('basicauth', basicauth)]
    authenticators = [('auth_tkt', auth_tkt),
                    ('htpasswd', htpasswd)]
    challengers = [('redirector', redirector),
                ('basicauth', basicauth)]
    mdproviders = []

    from repoze.who.classifiers import default_request_classifier
    from repoze.who.classifiers import default_challenge_decider
    log_stream = sys.stdout

    middleware = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream = log_stream,
        log_level = logging.DEBUG
        )
    return middleware


# Repoze auth

def add_auth_fancy(app, config):
    log.debug("Running repoze add_auth")

    translations = {
        'user_name'         : 'email_address',
        'users'             : 'people',
        'group_name'        : 'name',
        'groups'            : 'roles',
        'validate_password' : 'check_password',
    }

    return setup_sql_auth(app, Person, Role, None, meta.Session, 
                  login_handler = '/login/submit',
       logout_handler = '/logout',
       post_login_url = '/login/continue',
       post_logout_url = '/logout/continue',
       charset=None,
       cookie_secret = 'my_secret_word', translations=translations)

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
    

    form = FriendlyFormPlugin(
        '/login',
        '/login/submit',
        '/login/continue',
        '/logout',
        '/logout/continue',
        login_counter_name=None,
        rememberer_name='cookie',
        charset=None,
        #charset="iso-8859-1",
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


def redirect_auth_denial(reason):
    if response.status_int == 401:
        message = 'You are not logged in.'
        message_type = 'warning'
    else:
        message = 'You do not have the permissions to access this page.'
        message_type = 'error'

    #h.flash(message, message_type)
    redirect(url('/login', came_from=url.current()))

class ActionProtector(pylonshq.ActionProtector):
    default_denial_handler = staticmethod(redirect_auth_denial)

def has_organiser_role():
    return in_group('organiser').is_met(request.environ)

def has_reviewer_role():
    return in_group('reviewer').is_met(request.environ)
