import logging

from pylons import request, response, session, tmpl_context as c
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on

from formencode import validators, htmlfill
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.validators import BaseSchema, ReviewSchema
import zkpylons.lib.helpers as h

from zkpylons.lib.auth import ControllerProtector, ActionProtector, in_group, Predicate

from zkpylons.model import meta
from zkpylons.model import Review, Stream, Person, ProposalType, Proposal

log = logging.getLogger(__name__)

class is_reviewer(Predicate):
    message = "Must be review author"

    def evaluate(self, environ, credentials):
        """ Check if the logged in user authored the review """
        person_email = environ.get('REMOTE_USER')
        review_id = environ['pylons.routes_dict'].get('id')

        if person_email is None or review_id is None:
            self.unmet()

        review = Review.find_by_id(review_id, abort_404=False)
        if review is None or review.reviewer.email_address != person_email:
            self.unmet()

class is_proposer(Predicate):
    message = "Must be proposal author"

    def evaluate(self, environ, credentials):
        """ Check if the logged in user authored the proposal """
        person_email = environ.get('REMOTE_USER')
        review_id = environ['pylons.routes_dict'].get('id')

        if person_email is None or review_id is None:
            self.unmet()

        review = Review.find_by_id(review_id, abort_404=False)
        if review is None or person_email not in [p.email_address for p in review.proposal.people]:
            self.unmet()


@ControllerProtector(in_group('reviewer'))
class ReviewController(BaseController):
    def __before__(self, **kwargs):
        c.streams = Stream.select_values()

    @dispatch_on(POST="_edit") 
    def edit(self, id):
        c.review = Review.find_by_id(id)

        redirect_to(h.url_for(controller='proposal', id=c.review.proposal.id, action='review'))

    @ActionProtector(is_reviewer())
    @dispatch_on(POST="_delete")
    def delete(self, id):
        c.review = Review.find_by_id(id)

        return render('/review/confirm_delete.mako')

    @validate(schema=None, form='delete', post_only=True, on_get=True, variable_decode=True)
    def _delete(self, id):
        c.review = Review.find_by_id(id)

        meta.Session.delete(c.review)
        meta.Session.commit()

        h.flash("Review Deleted")
        redirect_to(controller='review', action='index')

    def summary(self):
        c.summary = Person.find_review_summary().all()
        return render('review/summary.mako')

    def index(self):
        c.proposal_type_collection = ProposalType.find_all()

        c.review_collection_by_type = {}
        for proposal_type in c.proposal_type_collection:
            query = Review.by_reviewer(h.signed_in_person()).join(Proposal).filter_by(proposal_type_id=proposal_type.id)
            c.review_collection_by_type[proposal_type] = query.all()
        return render('/review/list.mako')

    # Proposer can't view their own reviews, unless they are special
    @ActionProtector(h.auth.Any(h.auth.Not(is_proposer()), in_group('organiser')))
    def view(self, id):
        c.review = Review.find_by_id(id)

        if c.review is None:
            redirect_to(action='index')

        return render('review/view.mako')

