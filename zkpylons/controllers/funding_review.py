import logging

from pylons import request, response, session, tmpl_context as c
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on

from formencode import validators, htmlfill
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.validators import BaseSchema, FundingReviewSchema
import zkpylons.lib.helpers as h

from zkpylons.lib.auth import ControllerProtector, ActionProtector, in_group, Predicate

from zkpylons.lib.mail import email

from zkpylons.model import meta
from zkpylons.model import FundingReview

log = logging.getLogger(__name__)

class EditFundingReviewSchema(BaseSchema):
    review = FundingReviewSchema()
    pre_validators = [NestedVariables]

class is_reviewer(Predicate):
    message = "Review author"

    def evaluate(self, environ, credentials):
        """ Check if the logged in user authored the review """
        person_email = environ.get('REMOTE_USER')
        review_id = environ['pylons.routes_dict'].get('id')

        if person_email is None or review_id is None:
            self.unmet()

        if FundingReview.find_by_id(review_id, abort_404=False).reviewer.email_address != person_email:
            self.unmet()


@ControllerProtector(in_group('funding_reviewer'))
class FundingReviewController(BaseController):
    def __before__(self, **kwargs):
        return True

    @ActionProtector(is_reviewer())
    @dispatch_on(POST="_edit") 
    def edit(self, id):
        c.form = 'edit'
        c.review = FundingReview.find_by_id(id)
        c.funding = c.review.funding

        defaults = h.object_to_defaults(c.review, 'review')
        if defaults['review.score'] == None:
            defaults['review.score'] = 'null'
        if defaults['review.score'] == 1 or defaults['review.score'] == 2:
            defaults['review.score'] = '+%s'  % defaults['review.score']

        c.signed_in_person = h.signed_in_person()
        form = render('/funding_review/edit.mako')
        return htmlfill.render(form, defaults)

    @validate(schema=EditFundingReviewSchema(), form='edit', post_only=True, on_get=True, variable_decode=True)
    def _edit(self, id):
        c.review = FundingReview.find_by_id(id)

        if self.form_result['review']['score'] == 'null':
            self.form_result['review']['score'] = None

        for key in self.form_result['review']:
            setattr(c.review, key, self.form_result['review'][key])

        # update the objects with the validated form data
        meta.Session.commit()

        h.flash("Review has been edited!")
        redirect_to(action='view', id=id)

    @ActionProtector(is_reviewer())
    @dispatch_on(POST="_delete")
    def delete(self, id):
        c.review = FundingReview.find_by_id(id)
        
        return render('/funding_review/confirm_delete.mako')

    @validate(schema=None, form='delete', post_only=True, on_get=True, variable_decode=True)
    def _delete(self, id):
        c.review = FundingReview.find_by_id(id)

        meta.Session.delete(c.review)
        meta.Session.commit()

        h.flash("Review Deleted")
        redirect_to(controller='funding_review', action='index')

    def summary(self):
        c.review_collection=FundingReview.find_all()
        return render('funding_review/summary.mako')

    def index(self):
        c.review_collection = FundingReview.find_all()
        return render('funding_review/list.mako')

    def view(self, id):
        c.review = FundingReview.find_by_id(id)

        if c.review is None:
            redirect_to(action='index')

        return render('funding_review/view.mako')

