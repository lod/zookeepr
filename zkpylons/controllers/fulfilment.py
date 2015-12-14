import logging
import os
import tempfile

from pylons import request, response, session, tmpl_context as c, app_globals
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate, jsonify
from pylons.decorators.rest import dispatch_on

from formencode import validators, htmlfill, ForEach, Invalid
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.ssl_requirement import enforce_ssl
from zkpylons.lib.validators import BaseSchema, ExistingPersonValidator, FulfilmentTypeValidator, FulfilmentStatusValidator, FulfilmentTypeStatusValidator
import zkpylons.lib.helpers as h

from zkpylons.lib.mail import email

from zkpylons.lib.auth import ActionProtector, in_group

from zkpylons.model import meta, Fulfilment, FulfilmentType, FulfilmentStatus, FulfilmentGroup, Person
from zkpylons.model.config import Config

import zkpylons.lib.pdfgen as pdfgen

log = logging.getLogger(__name__)

class FulfilmentSchema(BaseSchema):
    person = ExistingPersonValidator()
    type = FulfilmentTypeValidator(not_empty=True)
    status = FulfilmentStatusValidator(not_empty=True)
    chained_validators = [FulfilmentTypeStatusValidator(type='type', status='status')]

class NewFulfilmentSchema(BaseSchema):
    fulfilment = FulfilmentSchema()
    pre_validators = [NestedVariables]

class EditFulfilmentSchema(BaseSchema):
    fulfilment = FulfilmentSchema()
    pre_validators = [NestedVariables]

class FulfilmentController(BaseController):

    @enforce_ssl(required_all=True)
    def __before__(self, **kwargs):
        c.can_edit = True

        c.fulfilment_type = FulfilmentType.find_all()
        c.fulfilment_status = FulfilmentStatus.find_all()

    @ActionProtector(in_group('organiser'))
    @dispatch_on(POST="_new")
    def new(self):
        return render('/fulfilment/new.mako')

    @validate(schema=NewFulfilmentSchema(), form='new', post_only=True, on_get=True, variable_decode=True)
    def _new(self):
        results = self.form_result['fulfilment']

        c.fulfilment = Fulfilment(**results)
        meta.Session.add(c.fulfilment)
        meta.Session.commit()

        h.flash("Fulfilment created")
        redirect_to(action='index', id=None)

    @ActionProtector(in_group('organiser'))
    def view(self, id):
        c.fulfilment = Fulfilment.find_by_id(id)
        return render('/fulfilment/view.mako')

    @ActionProtector(in_group('organiser'))
    def person(self, id):
        # TODO: This function breaks the URL model, id should be a fulfilment id
        c.person = Person.find_by_id(id)
        return render('/fulfilment/person.mako')

    @ActionProtector(in_group('organiser'))
    def index(self):
        c.fulfilment_collection = Fulfilment.find_all()
        return render('/fulfilment/list.mako')

    @ActionProtector(in_group('organiser'))
    @dispatch_on(POST="_edit")
    def edit(self, id):
        c.fulfilment = Fulfilment.find_by_id(id)

        defaults = h.object_to_defaults(c.fulfilment, 'fulfilment')
        defaults['fulfilment.person'] = c.fulfilment.person_id
        defaults['fulfilment.type'] = c.fulfilment.type_id
        defaults['fulfilment.status'] = c.fulfilment.status_id

        form = render('/fulfilment/edit.mako')
        return htmlfill.render(form, defaults)

    @ActionProtector(in_group('organiser'))
    @validate(schema=EditFulfilmentSchema(), form='edit', post_only=True, on_get=True, variable_decode=True)
    def _edit(self, id):
        fulfilment = Fulfilment.find_by_id(id)

        for key in self.form_result['fulfilment']:
            setattr(fulfilment, key, self.form_result['fulfilment'][key])

        # update the objects with the validated form data
        meta.Session.commit()
        h.flash("The Fulfilment has been updated successfully.")
        redirect_to(action='index', id=None)

    @ActionProtector(in_group('organiser'))
    @dispatch_on(POST="_delete")
    def delete(self, id):
        """Delete the fulfilment

        GET will return a form asking for approval.

        POST requests will delete the item.
        """
        c.fulfilment = Fulfilment.find_by_id(id)
        return render('/fulfilment/confirm_delete.mako')

    @ActionProtector(in_group('organiser'))
    @validate(schema=None, form='delete', post_only=True, on_get=True, variable_decode=True)
    def _delete(self, id):
        c.fulfilment = Fulfilment.find_by_id(id)
        meta.Session.delete(c.fulfilment)
        meta.Session.commit()

        h.flash("Fulfilment has been deleted.")
        redirect_to('index', id=None)

    @ActionProtector(in_group('checkin'))
    def _badge(self, id):
        c.fulfilment = Fulfilment.find_by_id(id)

        xml_s = render('/fulfilment/badge.mako')
        xsl_f = app_globals.mako_lookup.get_template('/fulfilment/badge.xsl').filename
        pdf_data = pdfgen.generate_pdf(xml_s, xsl_f)
        return pdf_data

    @ActionProtector(in_group('organiser'))
    def badge_pdf(self, id):
        pdf_data = self._badge(id)
        filename = Config.get('event_shortname') + '_' + str(c.fulfilment.id) + '.pdf'
        return pdfgen.wrap_pdf_response(pdf_data, filename)

    @ActionProtector(in_group('checkin'))
    def badge_print(self, id):
        pdf_data = self._badge(id)
        (output_fd, output_path) = tempfile.mkstemp('.pdf')
        os.write(output_fd, pdf_data)
        os.close(output_fd)

        #os.system('lpr' + output_path)
        if os.path.exists(output_path):
            os.remove(output_path)

        # TODO: This needs be unhardcoded
        c.fulfilment.status_id = 5
        meta.Session.commit()

    @ActionProtector(in_group('checkin'))
    def swag_give(self, id):
        c.fulfilment = Fulfilment.find_by_id(id)
        # TODO: This needs be unhardcoded
        c.fulfilment.status_id = 6
        meta.Session.commit()
