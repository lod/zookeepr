# Zookeepr driver for AuthKit
#
# This module allows us to use the authkit infrastructure but using the Zookeepr models to do so
#  * We don't support groups
#  * We don't support the creation methods as zookeepr does that already
#


import logging

from pylons.templating import render_mako as render
from pylons import tmpl_context as c
from pylons import request

from formencode import validators, htmlfill, Invalid
from zookeepr.lib.validators import BaseSchema

from zookeepr.model import meta
from zookeepr.model import Person, Role, Proposal, Invoice

from authkit.permissions import HasAuthKitRole, UserIn, NotAuthenticatedError, NotAuthorizedError, Permission
from authkit.authorize import PermissionSetupError, middleware
from authkit.authorize.pylons_adaptors import authorized


import md5

log = logging.getLogger(__name__)

class LoginSchema(BaseSchema):
    username = validators.Email(not_empty=True)
    password = validators.String(not_empty=True)

def render_signin(environ):
    if 'auth_failure' in environ:
        c.auth_failure = environ['auth_failure']
    else:
        c.auth_failure = None

    errors = {}
    defaults = dict(request.params)
    if defaults:
        try:
            LoginSchema.to_python(defaults)
        except Invalid, error:
            defaults = error.value
            errors = error.error_dict or {}

    form = render('/person/signin.mako')
    return htmlfill.render(form, defaults=defaults, errors=errors).replace('%', '%%').replace('FORM_ACTION', '%s')


def encrypt(password):
    return md5.new(password).hexdigest()


def valid_password(environ, username, password):
    """
    A function which can be used with the ``basic`` and ``form`` authentication
    methods to validate a username and passowrd.

    In this implementation usernames are case insensitive and passwords are
    case sensitive. The function returns ``True`` if the user ``username`` has
    the password specified by ``password`` and returns ``False`` if the user
    doesn't exist or the password is incorrect.
    """

    person = Person.find_by_email(username)

    if person is None:
        environ['auth_failure'] = 'NO_USER'
        return False

    if not person.activated:
        environ['auth_failure'] = 'NOT_ACTIVATED'
        return False

    if not person.check_password(password):
        environ['auth_failure'] = 'BAD_PASSWORD'
        return False

    return True


class ValidZookeeprUser(UserIn):
    """
    Checks that the signed in user is one of the users specified when setting up
    the user management API.
    """
    def __init__(self):
        pass

    def check(self, app, environ, start_response):

        if not environ.get('REMOTE_USER'):
            raise NotAuthenticatedError('Not Authenticated')

        person = Person.find_by_email(environ['REMOTE_USER'])
        if Person is None:
            environ['auth_failure'] = 'NO_USER'
            raise NotAuthorizedError(
                'You are not one of the users allowed to access this resource.'
            )
        return app(environ, start_response)

class HasZookeeprRole(HasAuthKitRole):
    def check(self, app, environ, start_response):
        """
        Should return True if the user has the role or
        False if the user doesn't exist or doesn't have the role.

        In this implementation role names are case insensitive.
        """

        if not environ.get('REMOTE_USER'):
            if self.error:
                raise self.error
            raise NotAuthenticatedError('Not authenticated')

        for role in self.roles:
           if not self.role_exists(role):
               raise Exception("No such role %r exists"%role)

        if self.all:
            for role in self.roles:
                if not self.user_has_role(environ['REMOTE_USER'], role):
                    if self.error:
                        raise self.error
                    else:
                        environ['auth_failure'] = 'NO_ROLE'
                        raise NotAuthorizedError(
                            "User doesn't have the role %s"%role.lower()
                        )
            return app(environ, start_response)
        else:
            for role in self.roles:
                if self.user_has_role(environ['REMOTE_USER'], role):
                    return app(environ, start_response)
            if self.error:
                raise self.error
            else:
                environ['auth_failure'] = 'NO_ROLE'
                raise NotAuthorizedError(
                    "User doesn't have any of the specified roles"
                )

    def user_exists(self, username):
        """
        Returns ``True`` if the user exists, ``False`` otherwise. Users are
        case insensitive.
        """

        person = Person.find_by_email(username)

        if person is not None:
            return True
        return False

    def role_exists(self, role):
        """
        Returns ``True`` if the role exists, ``False`` otherwise. Roles are
        case insensitive.
        """
        role = Role.find_by_name(role)

        if role is not None:
            return True
        return False

    def user_has_role(self, username, role):
        """
        Returns ``True`` if the user has the role specified, ``False``
        otherwise. Raises an exception if the user doesn't exist.
        """
        if not self.user_exists(username.lower()):
            raise AuthKitNoSuchUserError("No such user %r"%username.lower())
        if not self.role_exists(role.lower()):
            raise AuthKitNoSuchRoleError("No such role %r"%role.lower())
        person = Person.find_by_email(username)
        if person is None:
            return False

        for role_ in person.roles:
            if role_.name == role.lower():
                return True
        return False

class IsSameZookeeprUser(UserIn):
    """
    Checks that the signed in user is one of the users specified when setting up
    the user management API.
    """
    def __init__(self, id):
        self.id = int(id)

    def check(self, app, environ, start_response):

        if not environ.get('REMOTE_USER'):
            raise NotAuthenticatedError('Not Authenticated')

        person = Person.find_by_email(environ['REMOTE_USER'])
        if person is None:
            environ['auth_failure'] = 'NO_USER'
            raise NotAuthorizedError(
                'You are not one of the users allowed to access this resource.'
            )

        if self.id != person.id:
            environ['auth_failure'] = 'NO_ROLE'
            raise NotAuthorizedError(
                "User doesn't have any of the specified roles"
            )

        return app(environ, start_response)

class IsSameZookeeprSubmitter(UserIn):
    """
    Checks that the signed in user is one of the users specified when setting up
    the user management API.
    """
    def __init__(self, proposal_id):
        self.proposal_id = int(proposal_id)

    def check(self, app, environ, start_response):

        if not environ.get('REMOTE_USER'):
            raise NotAuthenticatedError('Not Authenticated')

        person = Person.find_by_email(environ['REMOTE_USER'])
        if person is None:
            environ['auth_failure'] = 'NO_USER'
            raise NotAuthorizedError(
                'You are not one of the users allowed to access this resource.'
            )

        proposal = Proposal.find_by_id(self.proposal_id)
        if proposal is None:
            raise NotAuthorizedError(
                "Proposal doesn't exist"
            )

        if person not in proposal.people:
            environ['auth_failure'] = 'NO_ROLE'
            raise NotAuthorizedError(
                "User doesn't have any of the specified roles"
            )

        return app(environ, start_response)

class IsSameZookeeprAttendee(UserIn):
    """
    Checks that the signed in user is the user for which the given invoice
    is for.
    """
    def __init__(self, invoice_id):
        self.invoice_id = int(invoice_id)

    def check(self, app, environ, start_response):

        if not environ.get('REMOTE_USER'):
            raise NotAuthenticatedError('Not Authenticated')

        person = Person.find_by_email(environ['REMOTE_USER'])
        if person is None:
            environ['auth_failure'] = 'NO_USER'
            raise NotAuthorizedError(
                'You are not one of the users allowed to access this resource.'
            )

        invoice = Invoice.find_by_id(self.invoice_id)
        if invoice is None:
            raise NotAuthorizedError(
                "Invoice doesn't exist"
            )

        if person.id <> invoice.person_id:
            environ['auth_failure'] = 'NO_ROLE'
            raise NotAuthorizedError(
                "Invoice is not for this user"
            )

        return app(environ, start_response)


class Or(Permission):
    """
    Checks all the permission objects listed as keyword arguments in turn.
    Permissions are checked from left to right. The error raised by the ``Or``
    permission is the error raised by the first permission check to fail.
    """

    def __init__(self, *permissions):
        if len(permissions) < 2:
            raise PermissionSetupError('Expected at least 2 permissions objects')
        permissions = list(permissions)
        self.permissions = permissions

    def check(self, app, environ, start_response):
        for permission in self.permissions:
            try:
                permission.check(app, environ, start_response)
                return app(environ, start_response)
            except NotAuthorizedError:
                pass


        raise NotAuthorizedError(
                'You are not one of the users allowed to access this resource.'
        )

def no_role():
    request.environ['auth_failure'] = 'NO_ROLE'
    raise NotAuthorizedError(
            "User doesn't have any of the specified roles"
            )



# Role shortcuts to save db work
has_organiser_role = HasZookeeprRole('organiser')
has_reviewer_role = HasZookeeprRole('reviewer')
has_papers_chair_role = HasZookeeprRole('papers_chair')
has_planetfeed_role = HasZookeeprRole('planetfeed')
has_keysigning_role = HasZookeeprRole('keysigning')
is_valid_user = ValidZookeeprUser()
is_same_zookeepr_user = IsSameZookeeprUser
is_same_zookeepr_submitter = IsSameZookeeprSubmitter
is_same_zookeepr_attendee = IsSameZookeeprAttendee
