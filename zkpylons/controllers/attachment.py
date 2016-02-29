import logging

from pylons import request, response, session, tmpl_context as c
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on
from pylons.controllers.util import abort

from formencode import validators, htmlfill, ForEach, Invalid
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.validators import BaseSchema, ProductValidator
import zkpylons.lib.helpers as h

from zkpylons.lib.auth import Predicate, in_group, Any, ControllerProtector, ActionProtector, is_activated

from zkpylons.lib.mail import email

from zkpylons.model import meta, Attachment, Proposal, Person

log = logging.getLogger(__name__)

class is_author(Predicate):
    message = u'You may only access your own proposals'
    def evaluate(self, environ, credentials):

        person_email = environ.get('REMOTE_USER')
        proposal_id = environ['pylons.routes_dict'].get('id')

        if proposal_id is None or person_email is None:
            self.unmet()

        person = Person.find_by_email(environ['REMOTE_USER'])
        attachment = Attachment.find_by_id(proposal_id, abort_404=False)
        if attachment is None or person is None:
            self.unmet()

        if person not in attachment.proposal.people:
            self.unmet()


@ControllerProtector(Any(in_group('organiser'), is_author()))
class AttachmentController(BaseController):
    def __before__(self, **kwargs):
        attachment_id = kwargs.get('id')
        if attachment_id is None:
            abort(404) # Page without id doesn't exist
        c.attachment = Attachment.find_by_id(attachment_id)
        if(c.attachment == None):
            abort(404) # Page with this id doesn't exist

    @dispatch_on(POST="_delete")
    def delete(self, id):
        c.proposal = c.attachment.proposal
        return render('/attachment/confirm_delete.mako')

    @validate(schema=None, form='delete', post_only=True, on_get=True, variable_decode=True)
    def _delete(self, id):
        proposal_id = c.attachment.proposal.id # Cache before deletion
        meta.Session.delete(c.attachment)
        meta.Session.commit()

        h.flash("Attachment Deleted")
        redirect_to(controller='proposal', action='view', id=proposal_id)

    def view(self, id):
        response.headers['content-type'] = c.attachment.content_type.encode('ascii','ignore')
        response.headers.add('content-transfer-encoding', 'binary')
        response.headers.add('content-length', len(c.attachment.content))
        response.headers['content-disposition'] = 'attachment; filename="%s";' % c.attachment.filename.encode('ascii','ignore')
        response.headers.add('Pragma', 'cache')
        response.headers.add('Cache-Control', 'max-age=3600,public')
        return c.attachment.content
