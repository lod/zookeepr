import pytest
import random

from routes import url_for

from zk.model import Person, Volunteer

from .fixtures import CompletePersonFactory, PersonFactory, RoleFactory, VolunteerFactory, ProductCategoryFactory, ConfigFactory, ProductFactory
from .utils import do_login
from .crud_helper import CrudHelper

class TestVolunteer(CrudHelper):
    @pytest.yield_fixture(autouse=True)
    def prep_questions(self, db_session):
        # Volunteer questions are set in a Config value
        self.questions = [
            {
                "title" : "Color of underpants",
                "questions" : [
                    {
                        "name" : "Red",
                        "description" : "Predominantly a red like colour",
                    },
                    {
                        "name" : "White",
                        "description" : "Mostly a shade of white",
                    },
                    {
                        "name" : "Black",
                        "description" : "Mostly a very dark shade of white",
                    },
                    {
                        "name" : "Cowboy Neal",
                        "description" : "Underpants are for the kind of weirdos who wear pants",
                    },
                ],
            },
            {
                "title" : "Opinion on jackfruit",
                "questions" : [
                    {
                        "name" : "WTF",
                        "description" : "Despite Jackfruit being a thing that is available to me through the modern marvels of refrigeration and transportation I have no idea what you are talking about",
                    },
                    {
                        "name" : "Too much",
                        "description" : "I love them but I can never finish the damn things",
                    },
                    {
                        "name" : "Underage",
                        "description" : "Eating an underage jackfruit you can almost taste the bloody tang of a life not lived, the tender meaty goodness of a fruit cut off before the prime of its life, the hard toughness of a fruit not yet ready to seed. Almost as good as veal."
                    },
                ],
            },
        ]
        ConfigFactory(category='rego', key='volunteer', value = self.questions)
        db_session.commit()
        yield

    def test_permissions(self, app, db_session, smtplib):
        ProductCategoryFactory(name='Ticket')

        activated = CompletePersonFactory()
        not_activated = CompletePersonFactory(activated=False)

        print "Require activated user"
        CrudHelper.test_permissions(self, app, db_session, 
            good_pers=activated, bad_pers=not_activated,
            get_pages=('new', 'edit', 'index'), post_pages=('new', 'edit')
        )

        print "Require organiser"
        CrudHelper.test_permissions(self, app, db_session, 
            get_pages=('view', 'accept', 'pending', 'reject'), post_pages=('accept',)
        )

        print "Require author"
        target = VolunteerFactory(person=activated)
        CrudHelper.test_permissions(self, app, db_session, get_pages=('view',), post_pages=[])


    def test_new(self, app, db_session, smtplib):

        volunteer = CompletePersonFactory()
        db_session.commit()

        answers = ["Red", 'White', 'Black', 'Cowboy_Neal', 'WTF', 'Too_much', 'Underage']

        data = {
            'other' : "I like painting cows",
            'experience' : "I've done a few freisians and an adaptaur",
        }

        areas = { k : random.choice([True, False]) for k in answers }

        def extra_form_check(form):
            for k in answers:
                assert 'volunteer.areas.'+k in form.fields

        def extra_form_set(form):
            for k in answers:
                form['volunteer.areas.'+k] = areas[k]

        def extra_data_check(new):
            selected = sorted([ k for k in answers if areas[k] ])
            entered = sorted(new.areas)
            assert selected == entered

        CrudHelper.test_new(self, app, db_session, user=volunteer, title="Volunteer", data=data, extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check)

        # A person can only volunteer once, second attempt should redirect to edit page
        resp = app.get(url_for(controller='volunteer', action='new', id=None))
        assert resp.status_code == 302
        assert url_for(controller='volunteer', action='edit', id=Person.find_by_id(volunteer.id).volunteer.id) in resp.location


    def test_view(self, app, db_session):

        # Volunteer has edit options not provided to organiser
        # Accepted string toggle
        # If organiser, personal details

        answers = ["Red", 'White', 'Black', 'Cowboy Neal', 'WTF', 'Too much', 'Underage']
        areas = [ random.choice(answers) for i in range(3) ]

        volunteer = CompletePersonFactory(roles=[RoleFactory(name="weirdrole"), RoleFactory(name="dummyrole")], phone="", mobile="", country="VollyLand")
        target = VolunteerFactory(person=volunteer, accepted=False, areas=areas, other="I like painting cows", experience="I have done a few freisians and an adaptaur")
        db_session.commit()

        expected = [
            target.other,
            target.experience,
        ] + areas + [ cat['title'] for cat in self.questions ] + [ q['description'] for cat in self.questions for q in cat['questions'] if q['name'] in areas ]

        accepted_only = [
            "Your application to be a volunteer has been accepted",
        ]
        organiser_only = [
            "Name:", volunteer.fullname,
            "Email:", # volunteer.email_address, - Email address listed in side bar
            "weirdrole",
            "dummyrole",
            "Country:", volunteer.country,
            "Reject", url_for(controller="volunteer", action="reject", id=target.id),
            url_for(controller="volunteer", action="accept", id=target.id),
        ]
        optional_fields = [
            "Mobile:",
            "Phone:",
        ]
        organiser_accepted = [
            "Change ticket", 
            "Pending", url_for(controller="volunteer", action="pending", id=target.id),
        ]
        organiser_not_accepted = [
            "Accept",
        ]
        volly_only = [
            "Edit", url_for(controller="volunteer", action="edit", id=target.id),
        ]

        resp = CrudHelper.test_view(self, app, db_session, user=volunteer, title="Volunteer Details", expected=expected+volly_only, target=target)

        for line in organiser_only + accepted_only + optional_fields + organiser_accepted + organiser_not_accepted:
            assert line not in unicode(resp.body, 'utf-8')

        target.accepted=True
        db_session.commit()
        
        resp = CrudHelper.test_view(self, app, db_session, user=volunteer, title="Volunteer Details", expected=expected+accepted_only+volly_only, target=target)

        for line in organiser_only + optional_fields + organiser_accepted + organiser_not_accepted:
            assert line not in unicode(resp.body, 'utf-8')

        # Switch to organiser
        resp = CrudHelper.test_view(self, app, db_session, title="Volunteer Details", expected=expected+accepted_only+organiser_only+organiser_accepted, target=target)

        for line in optional_fields+organiser_not_accepted:
            assert line not in unicode(resp.body, 'utf-8')

        volunteer.phone = "MightWeirdPhoneNumber"
        volunteer.mobile = "MobileMobile MobilePhone"
        optional_fields.append(volunteer.phone)
        optional_fields.append(volunteer.mobile)
        db_session.commit()

        resp = CrudHelper.test_view(self, app, db_session, title="Volunteer Details", expected=expected+accepted_only+organiser_only+optional_fields+organiser_accepted, target=target)


    def test_edit(self, app, db_session):

        volunteer = CompletePersonFactory()
        target = VolunteerFactory(person=volunteer, accepted=False, other="I like painting cows", experience="I have done a few freisians and an adaptaur")
        db_session.commit()

        answers = ["Red", 'White', 'Black', 'Cowboy_Neal', 'WTF', 'Too_much', 'Underage']

        initial_values = {
            'other' : target.other,
            'experience' : target.experience,
        }

        data = {
            'other' : "I have also ambitions to paint a kangaroo",
            'experience' : "I keep trying to catch them but they are sneaky buggers. I hit one with my car but the canvas was too torn up.",
        }

        areas = { k : random.choice([True, False]) for k in answers }

        def extra_form_set(form):
            for k in answers:
                form['volunteer.areas.'+k] = areas[k]

        def extra_data_check(new):
            selected = sorted([ k for k in answers if areas[k] ])
            entered = sorted(new.areas)
            assert selected == entered

        CrudHelper.test_edit(self, app, db_session, user=volunteer, title="Volunteer", target=target, initial_values=initial_values, new_values=data, extra_form_set=extra_form_set, extra_data_check=extra_data_check)


    def test_delete(self):
        pass # No delete option


    def test_index(self, app, db_session):

        targets = [VolunteerFactory() for i in range(10)]
        db_session.commit()

        # fullname and phone number are null
        # Other gets escaped, difficult to match so we skip it
        entries = { t.id : [t.person.email_address] for t in targets }

        entry_actions = ('accept', 'reject')

        CrudHelper.test_index(self, app, db_session, title="List of Volunteers", entries=entries, entry_actions=entry_actions, page_actions=[])


    def test_accept(self, app, db_session, smtplib):
        ticket = ProductCategoryFactory(name='Ticket')
        product1 = ProductFactory(category=ticket, description="Someone who has Volunteered")
        product2 = ProductFactory(category=ticket, description="Another Volunteer for the feed mill")
        product3 = ProductFactory(category=ticket, description="Please don't make me volunteer")
        user = PersonFactory(roles = [CrudHelper._get_insert_role('organiser')])
        target = VolunteerFactory(accepted=None, ticket_type=None)
        db_session.commit()

        do_login(app, user)
        resp = app.get(url_for(controller='volunteer', action='accept', id=target.id))
        print resp
        body = unicode(resp.body, 'utf-8')
        assert "Accept Volunteer" in body
        assert product1.description in body
        assert product2.description in body
        assert product3.description not in body
        assert "Please choose the ticket type that the volunteer will be eligible for" in body
        assert "No Ticket" in body

        f=resp.form
        f['ticket_type'] = product2.id
        post_resp = f.submit()
        print post_resp

        assert post_resp.status_code == 302
        assert url_for(controller='volunteer', action='index', id=None) in post_resp.location

        # Should send a acceptance email
        assert smtplib.existing is not None
        assert target.person.email_address in smtplib.existing.to_addresses

        message = smtplib.existing.message
        assert "You have not been selected as a volunteer" not in message
        assert "You have been accepted as a volunteer" in message
        assert "We will be in contact shortly" not in message

        target_id = target.id
        product_id = product2.id
        db_session.expunge_all()
        res = Volunteer.find_by_id(target_id)
        assert res.accepted == True
        assert res.ticket_type.id == product_id


    def test_pending(self, app, db_session):
        product = ProductFactory()
        user = PersonFactory(roles = [CrudHelper._get_insert_role('organiser')])
        target = VolunteerFactory(accepted=True, ticket_type=product)
        db_session.commit()

        do_login(app, user)
        resp = app.get(url_for(controller='volunteer', action='pending', id=target.id))
        assert resp.status_code == 302
        assert url_for(controller='volunteer', action='index', id=None) in resp.location

        target_id = target.id
        db_session.expunge_all()

        res = Volunteer.find_by_id(target_id)
        assert res.accepted == None
        assert res.ticket_type == None


    def test_reject(self, app, db_session, smtplib):
        product = ProductFactory()
        user = PersonFactory(roles = [CrudHelper._get_insert_role('organiser')])
        target = VolunteerFactory(accepted=True, ticket_type=product)
        db_session.commit()

        do_login(app, user)
        resp = app.get(url_for(controller='volunteer', action='reject', id=target.id))
        assert resp.status_code == 302
        assert url_for(controller='volunteer', action='index', id=None) in resp.location

        # Should send a rejection email
        assert smtplib.existing is not None
        assert target.person.email_address in smtplib.existing.to_addresses

        message = smtplib.existing.message
        assert "You have not been selected as a volunteer" in message
        assert "You have been accepted as a volunteer" not in message
        assert "We will be in contact shortly" not in message

        target_id = target.id
        db_session.expunge_all()
        res = Volunteer.find_by_id(target_id)
        assert res.accepted == False
        assert res.ticket_type == None
