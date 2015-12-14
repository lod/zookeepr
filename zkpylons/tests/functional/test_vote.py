import random

from .fixtures import faker, CompletePersonFactory, EventTypeFactory, LocationFactory, TimeSlotFactory, ScheduleFactory, EventFactory, RegistrationFactory
from .utils import do_login

class TestVote(object):
    """ Voting is used to select the best talk from the conference. """

    def test_new(self, app, db_session):
        """ new is a bit of an everything page, it displays a form and submits to
            itself with parameterised GET requests which it free-parses. """

        pres = EventTypeFactory(name='presentation')
        locs  = [LocationFactory() for i in range(4)]
        slots = [TimeSlotFactory() for i in range(10)]
        scheds = []
        for slot in slots:
            for loc in locs:
                scheds.append(ScheduleFactory(time_slot=slot, location=loc, event=EventFactory(type=pres, title=faker.word())))

        user = CompletePersonFactory()
        RegistrationFactory(person=user)

        db_session.commit()

        do_login(app, user)
        resp1 = app.get('/vote/new')
        body1 = unicode(resp1.body, 'utf-8')
        print resp1

        assert "You have 4 votes remaining" in body1
        for sched in scheds:
            assert sched.event.title in body1
            assert '"/vote/new?eventid=%d"' % sched.event.id in body1
        assert "revoke=1" not in body1

        # Vote for an event
        voted = [random.choice(scheds)]
        print "VOTING FOR %d" % voted[0].event.id
        resp2 = app.get('/vote/new?eventid=%d' % voted[0].event.id)
        body2 = unicode(resp2.body, 'utf-8')
        print resp2

        assert "You have 3 votes remaining" in body2
        for sched in scheds:
            assert sched.event.title in body2
            assert '"/vote/new?eventid=%d"' % sched.event.id in body2
        for v in voted:
            assert '"/vote/new?eventid=%d&revoke=1"' % v.event.id in body2

        # Vote for 3 more
        for i in range(3):
            r = random.choice(scheds)
            voted.append(r)
            app.get('/vote/new?eventid=%d' % r.event.id)

        resp3 = app.get('/vote/new')
        body3 = unicode(resp3.body, 'utf-8')
        print resp3

        assert "You have 0 votes remaining" in body3
        for sched in scheds:
            assert sched.event.title in body3
            # Vote links no longer shown
            assert '"/vote/new?eventid=%d"' % sched.event.id not in body3
        for v in voted:
            assert '"/vote/new?eventid=%d&revoke=1"' % v.event.id in body3

        # Revoke an entry
        revoke = random.choice(voted)
        voted.remove(revoke)
        resp4 = app.get('/vote/new?eventid=%d&revoke=1' % revoke.event.id)
        print resp4
        assert resp4.status_code == 302
        assert resp4.location.endswith('/vote/new')

        resp5 = resp4.follow()
        print resp5
        body5 = unicode(resp5.body, 'utf-8')

        assert "You have 1 votes remaining" in body5
        for sched in scheds:
            assert sched.event.title in body5
            assert '"/vote/new?eventid=%d"' % sched.event.id in body5
        for v in voted:
            assert '"/vote/new?eventid=%d&revoke=1"' % v.event.id in body5

