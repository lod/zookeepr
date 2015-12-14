import logging

from pylons import request, response, session, tmpl_context as c
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on

from formencode import validators, htmlfill
from formencode.variabledecode import NestedVariables

from zkpylons.lib.base import BaseController, render
from zkpylons.lib.ssl_requirement import enforce_ssl
from zkpylons.lib.validators import BaseSchema, ExistingRegistrationValidator, ExistingPersonValidator
import zkpylons.lib.helpers as h

from zkpylons.lib.auth import ActionProtector, ControllerProtector, not_anonymous, Predicate, get_person

from zkpylons.model import meta, Vote, Person, Event, EventType, Schedule, TimeSlot
from zkpylons.model.event import EventValidator

log = logging.getLogger(__name__)

class VoteSchema(BaseSchema):
    rego_id = ExistingRegistrationValidator(not_empty=True)

class NewVoteSchema(BaseSchema):
    vote = VoteSchema()
    pre_validators = [NestedVariables]

class UpdateVoteSchema(BaseSchema):
    vote = VoteSchema()
    pre_validators = [NestedVariables]

class is_registered(Predicate):
    message = "registered"

    def evaluate(self, environ, credentials):
        """ Check if the logged in user is registered """
        person = get_person()
        if person is None or person.registration is None:
            self.unmet()

# TODO: Pages other than new don't really make sense and should probably be ditched

@ControllerProtector(not_anonymous())
class VoteController(BaseController):

    @ActionProtector(is_registered())
    @dispatch_on(POST="_new")
    def new(self):
        user = h.signed_in_person()

        # Get parameters - TODO: Should be brought in through route
        eventid = request.GET.get('eventid',0)
        revoke = request.GET.get('revoke',0)

        c.events = Event.find_all()
        c.schedule = Schedule.find_all()
        c.time_slot = TimeSlot.find_all()

        c.votes = Vote.find_by_rego(user.registration.id)

        defaults = {
            'vote.vote_value': 1
        }

        if int(eventid) != 0 and c.votes.count() < 4 and revoke == 0:
            vote = Vote()
            vote.rego_id = user.registration.id
            vote.vote_value = 1
            vote.event_id = eventid
            meta.Session.add(vote)
            meta.Session.commit()

        if int(eventid) != 0 and int(revoke) != 0:
            vote = Vote.find_by_event_rego(eventid,user.registration.id)
            meta.Session.delete(vote)
            meta.Session.commit()
            redirect_to('new')

        form = render('/vote/new.mako')
        return htmlfill.render(form, defaults)

    @validate(schema=NewVoteSchema(), form='new', post_only=True, on_get=True, variable_decode=True)
    def _new(self):
        results = self.form_result['vote']

        c.vote = Vote(**results)
        meta.Session.add(c.vote)
        meta.Session.commit()

        h.flash("Vote created")
        redirect_to(action='view', id=c.vote.id)

    def index(self):
        redirect_to(action='new')

    @dispatch_on(POST="_edit")
    def edit(self, id):
        c.vote = Vote.find_by_id(id)

        defaults = h.object_to_defaults(c.vote, 'vote')

        form = render('vote/edit.mako')
        return htmlfill.render(form, defaults)

    @validate(schema=UpdateVoteSchema(), form='edit', post_only=True, on_get=True, variable_decode=True)
    def _edit(self, id):
        vote = Vote.find_by_id(id)

        for key in self.form_result['vote']:
            setattr(vote, key, self.form_result['vote'][key])

        # update the objects with the validated form data
        meta.Session.commit()
        h.flash("The note has been updated successfully.")
        redirect_to(action='view', id=id)

    @dispatch_on(POST="_revoke")
    def revoke(self):
        """Delete the rego note

        GET will return a form asking for approval.

        POST requests will delete the item.
        """
        args = request.GET
        eventid = int(args.get('eventid',0))
        c.signed_in_person = h.signed_in_person()
        c.vote = Vote.find_by_event_rego(eventid,c.signed_in_person.registration.id)
        meta.Session.delete(c.vote)
        meta.Session.commit()
        form = render('/vote/delete.mako')
        return htmlfill.render(form, defaults)
        redirect_to('new')

    @validate(schema=None, form='revoke', post_only=True, on_get=True, variable_decode=True)
    def _revoke(self):
        args = request.GET
        eventid = int(args.get('eventid',0))
        c.signed_in_person = h.signed_in_person()
        c.vote = Vote.find_by_event_rego(eventid,c.signed_in_person.registration.id)
        meta.Session.delete(c.vote)
        meta.Session.commit()
        redirect_to('new')


