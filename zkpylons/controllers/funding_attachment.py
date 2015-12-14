import logging

from pylons import request, response, session, tmpl_context as c
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on

from formencode import validators, htmlfill, ForEach, Invalid
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.validators import BaseSchema
import zkpylons.lib.helpers as h

from zkpylons.lib.auth import ControllerProtector, ActionProtector, in_group, Predicate

from zkpylons.model import meta
from zkpylons.model import Funding, FundingAttachment

log = logging.getLogger(__name__)

class is_owner(Predicate):
    message = "Owner of funding request"

    def evaluate(self, environ, credentials):
        """ Check if the funding attachment's funding request submitter matches the logged in user """

        person_email = environ.get('REMOTE_USER')
        attachment_id = environ['pylons.routes_dict'].get('id')

        if person_email is None or attachment_id is None:
            self.unmet()

        funding_email = FundingAttachment.find_by_id(attachment_id, abort_404=False).funding.person.email_address

        if funding_email != person_email:
            self.unmet()


@ControllerProtector(h.auth.is_activated())
class FundingAttachmentController(BaseController):

    @ActionProtector(h.auth.Any(in_group('organiser'), is_owner()))
    @dispatch_on(POST="_delete")
    def delete(self, id):
        c.attachment = FundingAttachment.find_by_id(id)
        c.funding = Funding.find_by_id(c.attachment.funding_id)
        
        return render('/funding_attachment/confirm_delete.mako')

    @validate(schema=None, form='delete', post_only=True, on_get=True, variable_decode=True)
    def _delete(self, id):
        attachment = FundingAttachment.find_by_id(id)
        funding_id = attachment.funding_id

        meta.Session.delete(attachment)
        meta.Session.commit()

        h.flash("Attachment Deleted")
        redirect_to(controller='funding', action='view', id=funding_id)

    @ActionProtector(h.auth.Any(in_group('organiser'), in_group('funding_reviewer'), is_owner()))
    def view(self, id):
        attachment = FundingAttachment.find_by_id(id)

        response.headers['content-type'] = attachment.content_type
        response.headers.add('content-transfer-encoding', 'binary')
        response.headers.add('content-length', len(attachment.content))
        response.headers['content-disposition'] = 'attachment; filename="%s";' % attachment.filename
        response.headers.add('Pragma', 'cache')
        response.headers.add('Cache-Control', 'max-age=3600,public')
        return attachment.content
