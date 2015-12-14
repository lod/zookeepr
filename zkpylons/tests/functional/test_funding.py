import random

from BeautifulSoup import BeautifulSoup
from routes import url_for

from zk.model import Config, Person, Funding

from .crud_helper import CrudHelper
from .fixtures import FulfilmentStatusFactory, FulfilmentTypeFactory, PersonFactory, FulfilmentGroupFactory
from .fixtures import RoleFactory, PersonFactory, CompletePersonFactory, FundingReviewFactory
from .fixtures import FundingFactory, ConfigFactory, FundingStatusFactory, FundingTypeFactory, FundingAttachment

from .utils import do_login


class TestFunding(CrudHelper):
    def test_permissions(self, app, db_session, smtplib):

        # Required permissions
        #######################
        # Activated: new, _new,
        # Submitter or organiser: attach, _attach, edit, _edit, withdraw, _withdraw, 
        # submitter, organiser, reviewer: view
        # organiser: approve, _approve, 
        # reviewer: review, _review, review_index, summary

        # activated: new, _new
        # submitter: new, _new, attach, _attach, edit, _edit, withdraw, _withdraw, view
        # reviewer: new, _new, view, review, _review, review_index, summary
        # organiser: new, _new, attach, _attach, edit, _edit, withdraw, _withdraw, view, approve, _approve

        unactivated = CompletePersonFactory(activated=False)
        activated   = CompletePersonFactory()
        submitter   = CompletePersonFactory()
        reviewer    = CompletePersonFactory(roles=[CrudHelper._get_insert_role('funding_reviewer')])
        organiser   = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])

        FundingStatusFactory(name='Withdrawn') # Required by model code
        target = FundingFactory(person=submitter)
        db_session.commit()

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=activated, bad_pers=unactivated,
                get_pages=('new',),
                post_pages=('new',)
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=submitter, bad_pers=activated,
                get_pages=('attach', 'edit', 'withdraw', 'view'),
                post_pages=('attach', 'edit', 'withdraw')
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=reviewer, bad_pers=activated,
                get_pages=('view', 'review', 'review_index', 'summary'),
                post_pages=('review', ),
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=organiser, bad_pers=activated,
                get_pages=('view', 'attach', 'edit', 'withdraw', 'view', 'approve'),
                post_pages=('attach', 'edit', 'withdraw', 'approve'),
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=organiser, bad_pers=reviewer,
                get_pages=('attach', 'edit', 'withdraw', 'approve'),
                post_pages=('attach', 'edit', 'withdraw', 'approve'),
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=reviewer, bad_pers=organiser,
                get_pages=('review', 'review_index', 'summary'),
                post_pages=('review', ),
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=reviewer, bad_pers=submitter,
                get_pages=('review', 'review_index', 'summary'),
                post_pages=('review', ),
        )


    def test_new(self, app, db_session, smtplib):
        # Funding status must be open

        # Try closed
        ConfigFactory(category='general', key='funding_status', value='closed')
        activated   = CompletePersonFactory(activated=True)
        db_session.commit()

        expected = [ "The funding application period is now closed" ]
        url = url_for(controller='funding', action='new', id=None)
        CrudHelper.test_view(self, app, db_session, url=url, user=activated, title="Closed", expected=expected)

        Config.find_by_pk(('general','funding_status')).value = 'not_open'
        db_session.commit()

        expected = [ "Funding requests can not be submitted yet" ]
        CrudHelper.test_view(self, app, db_session, url=url, user=activated, title="Coming soon", expected=expected)

        Config.find_by_pk(('general','funding_status')).value = 'open'
        ConfigFactory(category='rego', key='past_confs', value= [ ["01", "Mars"], ["03", "Venus"], ["05", "Jupiter"]])
        FundingStatusFactory(name='Pending')
        types = [ FundingTypeFactory(active=True) for i in range(10) ]

        data = {
                'type' : types[3].id,
                'male' : 1,
                'diverse_groups' : "As a white middle class first world male I represent a small minority of the world's population, less than one percent. And while I am overrepresented in the tech community, the wealth community, parliament and essentially every other forum where significant decisions are made I didn't get there by dint of hard work. Getting money and other benefits by virtue of my position is how I have gotten where I am in life and I feel you should continue it.",
                'how_contribute' : "I leach like a Patagonian toothfish with dentures",
                'financial_circumstances' : "I'm not going to stay this wealthy if I keep spending money",
                'supporting_information' : "I once gave a kid at school a wedgie just for wearing glasses, I'm not saying this is a threat but do you wear glasses?",
                'why_attend' : "I just like collecting free stuff, if you give me a ticket I probably won't actually show up but being handed stuff makes me feel better.",
        }

        def extra_form_check(f):
            assert 'funding.prevlca.01' in f.fields
            assert 'funding.prevlca.03' in f.fields
            assert 'funding.prevlca.05' in f.fields

            assert 'attachment1' in f.fields
            assert 'attachment2' in f.fields

        def extra_form_set(f):
            f['funding.prevlca.01'] = True
            f['funding.prevlca.03'] = False
            f['funding.prevlca.05'] = True

            f['attachment1'] = "testfile.txt", b'Really require an attachment?', "text/dummy"
            f['attachment2'] = "filetest.txt", b'Can\' figure out how to feed without one', "dummy/dummy"

        def extra_data_check(new):
            assert sorted(new.prevlca) == ['01', '05']

            assert len(new.attachments) == 2

            attach = new.attachments[0]
            assert attach.funding_id == new.id
            assert attach.filename == "testfile.txt"
            #assert attach.content_type == "text/dummy" # Always set to a constant, unsure why
            assert attach.content_type == "application/octet-stream"
            assert attach.content == b'Really require an attachment?'

            attach = new.attachments[1]
            assert attach.funding_id == new.id
            assert attach.filename == "filetest.txt"
            #assert attach.content_type == "text/dummy" # Always set to a constant, unsure why
            assert attach.content_type == "application/octet-stream"
            assert attach.content == b'Can\' figure out how to feed without one'
        
        CrudHelper.test_new(self, app, db_session, title="Funding Application", user=activated, data=data,
                extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check)

        # Ensure that confirmation email was sent
        assert smtplib.existing is not None
        assert "Thank you for submitting" in smtplib.existing.message
        assert "If you have any queries about your funding request" in smtplib.existing.message
        smtplib.existing.reset()


        # Late submitter can still submit when closed
        Config.find_by_pk(('general','funding_status')).value = 'closed'
        late = CompletePersonFactory(activated=True, roles = [RoleFactory(name='late_submitter')])
        db_session.commit()

        CrudHelper.test_new(self, app, db_session, title="Funding Application", user=late, data=data,
                extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check)


    def test_attach(self, app, db_session):
        organiser   = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])
        target = FundingFactory()
        db_session.commit()

        do_login(app, organiser)

        resp = app.get(url_for(controller='funding', action='attach', id=target.id))
        print resp
        body = unicode(resp.body, 'utf-8')
        assert "Attach a file" in body
        f = resp.form
        print f.fields
        f['attachment'] = "testfile.txt", b'Shovel in an attachment'
        post_resp = f.submit()
        print post_resp

        new = sorted(FundingAttachment.find_all(), key=lambda o: o.id)[-1]
        assert new.filename == "testfile.txt"
        assert new.content == b'Shovel in an attachment'
        assert new.content_type == "application/octet-stream"
        assert new.funding_id == target.id

        assert post_resp.status_code == 302
        assert url_for(controller='funding', action='view', id=new.id) in post_resp.location


    def test_view(self, app, db_session):
        ConfigFactory(category='rego', key='past_confs', value= [ ["01", "Mars"], ["03", "Venus"], ["05", "Jupiter"]])
        submitter   = CompletePersonFactory()
        target = FundingFactory(person=submitter)
        db_session.commit()

        expected = [target.type.name, target.person.fullname, target.person.email_address, ("Male" if target.male else "Female"), target.diverse_groups, target.how_contribute, target.financial_circumstances, target.supporting_information, target.why_attend] + 'Mars Venus Jupiter'.split(' ') + [ a.filename for a in target.attachments ]
        print expected
        resp = CrudHelper.test_view(self, app, db_session, title=target.type.name, user=submitter, target=target, expected=expected)
        assert "Reviews" not in resp

        # Funding reviewers and organisers see extra shit
        reviewer = CompletePersonFactory(roles=[CrudHelper._get_insert_role('funding_reviewer')])
        reviews = [ FundingReviewFactory(funding=target) for i in range(5) ]
        db_session.commit()

        more = ["Reviews"] + [ r.reviewer.fullname for r in reviews ] + [ r.comment for r in reviews ]
        CrudHelper.test_view(self, app, db_session, title=target.type.name, user=reviewer, target=target, expected=expected+more)


    def test_edit(self, app, db_session, smtplib):
        # Funding editing must be open for editing to work

        # Try closed
        ConfigFactory(category='general', key='funding_editing', value='closed')
        submitter   = CompletePersonFactory(activated=True)
        types = [ FundingTypeFactory(active=True) for i in range(10) ]
        target = FundingFactory(person=submitter, type=random.choice(types))
        db_session.commit()

        expected = [ "Editing has been disabled while funding requests are reviewed" ]
        url = url_for(controller='funding', action='edit', id=target.id)
        CrudHelper.test_view(self, app, db_session, user=submitter, url=url, title="Closed", expected=expected)

        # Even late_submitter can't edit when closed
        submitter.roles = [RoleFactory(name='late_submitter')]
        db_session.commit()

        CrudHelper.test_view(self, app, db_session, user=submitter, url=url, title="Closed", expected=expected)


        Config.find_by_pk(('general','funding_editing')).value = 'not_open'
        db_session.commit()

        expected = [ "The funding requests have not yet opened" ]
        CrudHelper.test_view(self, app, db_session, user=submitter, url=url, title="Coming soon", expected=expected)

        Config.find_by_pk(('general','funding_editing')).value = 'open'
        ConfigFactory(category='rego', key='past_confs', value= [ ["01", "Mars"], ["03", "Venus"], ["05", "Jupiter"]])
        FundingStatusFactory(name='Pending')

        initial = {
                'type' : str(target.type.id),
                'male' : str(int(target.male)),
                'diverse_groups' : target.diverse_groups,
                'how_contribute' : target.how_contribute,
                'financial_circumstances' : target.financial_circumstances,
                'supporting_information' : target.supporting_information,
                'why_attend' : target.why_attend,
        }

        data = {
                'type' : types[3].id,
                'male' : 1,
                'diverse_groups' : "As a white middle class first world male I represent a small minority of the world's population, less than one percent. And while I am overrepresented in the tech community, the wealth community, parliament and essentially every other forum where significant decisions are made I didn't get there by dint of hard work. Getting money and other benefits by virtue of my position is how I have gotten where I am in life and I feel you should continue it.",
                'how_contribute' : "I leach like a Patagonian toothfish with dentures",
                'financial_circumstances' : "I'm not going to stay this wealthy if I keep spending money",
                'supporting_information' : "I once gave a kid at school a wedgie just for wearing glasses, I'm not saying this is a threat but do you wear glasses?",
                'why_attend' : "I just like collecting free stuff, if you give me a ticket I probably won't actually show up but being handed stuff makes me feel better.",
        }

        def extra_form_check(f):
            assert 'funding.prevlca.01' in f.fields
            assert 'funding.prevlca.03' in f.fields
            assert 'funding.prevlca.05' in f.fields
            assert f['funding.prevlca.01'].value is None
            assert f['funding.prevlca.03'].value is None
            assert f['funding.prevlca.05'].value is None

            assert 'attachment' in f.fields
            assert 'attachment1' not in f.fields

        def extra_form_set(f):
            f['funding.prevlca.01'] = True
            f['funding.prevlca.03'] = False
            f['funding.prevlca.05'] = True

        def extra_data_check(new):
            assert sorted(new.prevlca) == ['01', '05']
            assert len(new.attachments) == 0

        CrudHelper.test_edit(self, app, db_session, title="Edit Funding Request", user=submitter, target=target, initial_values=initial, new_values=data,
                extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check)

        # Ensure that email was not sent
        assert smtplib.existing is None


    def test_index(self, app, db_session):
        # Index only lists your submitted funding requests
        ConfigFactory(category='general', key='funding_status', value='open')
        ConfigFactory(category='general', key='funding_editing', value='closed')
        status_strings = 'Pending Accepted Withdrawn Declined'.split(' ')
        submitter   = CompletePersonFactory()
        statuses = [ FundingStatusFactory(name=ss) for ss in status_strings ]
        targets = [ FundingFactory(person=submitter, status=random.choice(statuses)) for i in range(10) ]
        db_session.commit()

        def status_to_string(status):
            if status.name == 'Pending':
                return 'Undergoing review'
            else:
                return status.name

        entries = { t.id : [ t.type.name, status_to_string(t.status) ] for t in targets }
        print entries

        # Edit is only listed when status is Pending or Accepted and funding_editing is open
        # Withdraw is only listed when status is Pending or Accepted
        resp1 = CrudHelper.test_index(self, app, db_session, user=submitter, title="My Funding Applications", entries=entries, entry_actions = ('view', ))
        body1 = unicode(resp1.body, 'utf-8')

        # Ensure edit not present and withdraw present only when appropriate
        assert "Funding editing has been disabled" in body1
        for target in targets:
            assert url_for(controller='funding', action='edit', id=target.id) not in body1
        for target in targets:
            if target.status.name == 'Pending' or target.status.name == 'Accepted':
                assert url_for(controller='funding', action='withdraw', id=target.id) in body1
            else:
                assert url_for(controller='funding', action='withdraw', id=target.id) not in body1

        # Set funding_editing, should see edit when Pending or Accepted
        Config.find_by_pk(('general','funding_editing')).value = 'open'
        db_session.commit()
        resp2 = CrudHelper.test_index(self, app, db_session, user=submitter, title="My Funding Applications", entries=entries, entry_actions = ('view', ))
        body2 = unicode(resp2.body, 'utf-8')

        assert "Funding editing has been disabled" not in body2
        for target in targets:
            if target.status.name == 'Pending' or target.status.name == 'Accepted':
                assert url_for(controller='funding', action='edit', id=target.id) in body2
                assert url_for(controller='funding', action='withdraw', id=target.id) in body2
            else:
                assert url_for(controller='funding', action='edit', id=target.id) not in body2
                assert url_for(controller='funding', action='withdraw', id=target.id) not in body2

        # Set all pending, should always see withdraw and edit
        for target in targets:
            target.status = statuses[0] # First entry == Pending
        db_session.commit()
        entries = { t.id : [ t.type.name, status_to_string(t.status) ] for t in targets }
        resp3 = CrudHelper.test_index(self, app, db_session, user=submitter, title="My Funding Applications", entries=entries, entry_actions = ('view', 'edit', 'withdraw'))
        body3 = unicode(resp3.body, 'utf-8')

        assert "Funding editing has been disabled" not in body3

        # Setting funding_status to closed should hide new option
        Config.find_by_pk(('general','funding_status')).value = 'closed'
        resp4 = CrudHelper.test_index(self, app, db_session, user=submitter, title="My Funding Applications", entries=entries, entry_actions = ('view', 'withdraw', 'edit'), page_actions=[])
        body4 = unicode(resp4.body, 'utf-8')

        assert url_for(controller='funding', action='new', id=None) not in body4


    def test_approve(self, app, db_session):
        """ Approve shows a list of all funding requests.
            One column of each row contains the current state.
            The next column has a combo box with all other possible states or a no-change option.
            On submit all requests have their state updated.
        """
        status_strings = 'Pending Accepted Withdrawn Declined'.split(' ')
        statuses = [ FundingStatusFactory(name=ss) for ss in status_strings ]
        targets = [ FundingFactory(status=random.choice(statuses)) for i in range(50) ]
        db_session.commit()

        entries = { t.id : [ t.person.fullname, t.type.name, t.status.name ] for t in targets }

        resp = CrudHelper.test_index(self, app, db_session, title="Approve/disapprove funding", entries=entries, entry_actions=[], page_actions=[], url=url_for(controller='funding', action='approve', id=None))

        table = BeautifulSoup(resp.body).find('table')
        print table
        
        # Col0 = id, Col1 = fullname, Col2 = typename, Col3=CurStatus, Col4=StatusCombo
        for row in table.find('tbody').findAll('tr'):
            cells = row.findAll('td')
            id = int(cells[0].getText())
            status = cells[3].getText()
            assert Funding.find_by_id(id).status.name == status

        new_states = { t.id : random.choice(statuses) for t in targets }
        print new_states

        f = resp.form

        for t in targets:
            new = new_states[t.id]
            if new != t.status:
                print "UPDATE %d %s -> %s" % (t.id, t.status.name, new.name)
            else:
                print "CONST  %d %s -> %s" % (t.id, t.status.name, new.name)
            if new != t.status:
                f['status-%d' % t.id] = new.id

        post_resp = f.submit()
        print post_resp

        # Post shows the approve page again, new statuses should be reflected
        table = BeautifulSoup(post_resp.body).find('table')
        print table
        
        # Col0 = id, Col1 = fullname, Col2 = typename, Col3=CurStatus, Col4=StatusCombo
        for row in table.find('tbody').findAll('tr'):
            cells = row.findAll('td')
            id = int(cells[0].getText())
            status = cells[3].getText()
            assert new_states[id].name == status

        db_session.expunge_all()

        for id in new_states:
            assert Funding.find_by_id(id).status.id == new_states[id].id


    def test_withdraw(self, app, db_session, smtplib):
        """ Withdraw shows a basic confirmation page """
        FundingStatusFactory(name='Withdrawn')
        user = PersonFactory(roles = [self._get_insert_role('organiser')])
        target = FundingFactory( type=FundingTypeFactory(notify_email="bob@sees.all") )
        db_session.commit()

        do_login(app, user)
        resp = app.get(url_for(controller='funding', action='withdraw', id=target.id))
        body = unicode(resp.body, 'utf-8')

        assert "Withdraw this funding request" in body
        assert "Are you sure" in body

        post_resp = resp.form.submit()
        assert post_resp.status_code == 302
        assert url_for(controller='funding', action="index", id=None) in post_resp.location

        id = target.id
        db_session.expunge_all()
        assert Funding.find_by_id(id).status.name == 'Withdrawn'

        # Ensure that email is sent to organisers notifying of withdrawal
        assert smtplib.existing is not None
        assert "To: bob@sees.all" in smtplib.existing.message 
        assert "has withdrawn their funding request" in smtplib.existing.message

    def test_review(self, app, db_session):
        """ Review page shows the view page contents and then a form to enter the review """

        ConfigFactory(category='rego', key='past_confs', value= [ ["01", "Mars"], ["03", "Venus"], ["05", "Jupiter"]])
        FundingStatusFactory(name='Withdrawn')
        reviewer = CompletePersonFactory(roles=[CrudHelper._get_insert_role('funding_reviewer')])
        target = FundingFactory()
        reviews = [ FundingReviewFactory(funding=target) for i in range(5) ]
        db_session.commit()

        expected = [target.type.name, target.person.fullname, target.person.email_address, ("Male" if target.male else "Female"), target.diverse_groups, target.how_contribute, target.financial_circumstances, target.supporting_information, target.why_attend] + 'Mars Venus Jupiter'.split(' ') + [ a.filename for a in target.attachments ] + ["Reviews", url_for(controller='person', action='view', id=target.person.id), "stalk"] + [ r.reviewer.fullname for r in reviews ] + [ r.comment for r in reviews ]
        print expected

        resp = CrudHelper.test_view(self, app, db_session, title="Funding Application Review",  user=reviewer, target=target, expected=expected, url=url_for(controller='funding', action='review', id=target.id))
        f = resp.form

        assert 'review.score' in f.fields
        assert 'review.comment' in f.fields
        f['review.score'] = '+2'
        f['review.comment'] = 'I just like the idea of a randomly generated talk'
        post_resp = f.submit()

        # Only one funding request, so we should go back to the index
        assert post_resp.status_code == 302
        assert url_for(controller='funding', action='review_index', id=None) in post_resp.location

        resp2 = CrudHelper.test_view(self, app, db_session, title="Funding Application Review",  user=reviewer, target=target, expected=expected, url=url_for(controller='funding', action='review', id=target.id))
        # Can edit but not re-review -> No form fields
        assert len(resp2.form.fields) == 0
        assert 'You have already reviewed this funding request' in unicode(resp2.body, 'utf-8')


    def test_review_index(self, app, db_session):
        """ Lists all funding applications that the reviewer has not yet reviewed.
            List is in order of least reviews first, randomised among equals.
            Grouped by funding type.
        """

        ConfigFactory(category='rego', key='past_confs', value= [ ["01", "Mars"], ["03", "Venus"], ["05", "Jupiter"]])
        status_strings = 'Pending Accepted Withdrawn Declined'.split(' ')
        statuses = [ FundingStatusFactory(name=ss) for ss in status_strings ]
        types = [ FundingTypeFactory() for i in range(3) ]
        reviewer_role = CrudHelper._get_insert_role('funding_reviewer')
        reviewer = CompletePersonFactory(roles=[reviewer_role])
        reqs = [ FundingFactory(status=random.choice(statuses), type=random.choice(types)) for i in range(50) ]
        other_reviewers = [ CompletePersonFactory(roles=[reviewer_role]) for i in range(10) ]
        # Each reviewer can only review a proposal once
        for rev in other_reviewers:
            for req in random.sample(reqs, random.randint(30,40)):
                FundingReviewFactory(score=random.randint(-2,2), funding=req, reviewer=rev)
        # We have already reviewed a bunch of entries
        for req in random.sample(reqs, random.randint(5,15)):
            FundingReviewFactory(score=random.randint(-2,2), funding=req, reviewer=reviewer)

        db_session.commit()

        do_login(app, reviewer)
        resp = app.get(url_for(controller='funding', action='review_index', id=None))
        body = unicode(resp.body, 'utf-8')
        tables = BeautifulSoup(resp.body).findAll('table')
        assert len(tables) == len(types)

        assert "Funding Applications You Haven't Reviewed" in body
        for table in tables:
            # A table for each funding type
            # Each row contains: id, submitter.fullname, submission time, # reviews, review link
            # Don't show rows that we have reviewed
            for row in table.find('tbody').findAll('tr'):
                cells = row.findAll('td')
                id = cells[0].getText()
                req = Funding.find_by_id(id)
                assert req.person.fullname in str(cells[1])
                assert str(len(req.reviews)) in str(cells[3])
                assert url_for(controller='funding', action='review', id=id) in str(cells[4])
                assert reviewer not in [r.reviewer for r in req.reviews]
                assert req.status.name != 'Withdrawn'


    def test_summary(self, app, db_session):
        """ Summary lists the results of all the funding requests.
            Each funding request type has a table, one row per request.
            Any unreviewed request is skipped
            Each row contains the average score and details/comments
            Rows are sorted by average score, highest to lowest
        """

        status_strings = 'Pending Accepted Withdrawn Declined'.split(' ')
        statuses = [ FundingStatusFactory(name=ss) for ss in status_strings ]
        types = [ FundingTypeFactory() for i in range(3) ]
        reviewer_role = CrudHelper._get_insert_role('funding_reviewer')
        reqs = [ FundingFactory(status=random.choice(statuses), type=random.choice(types)) for i in range(50) ]
        reviewers = [ CompletePersonFactory(roles=[reviewer_role]) for i in range(10) ]
        # Each reviewer can only review a proposal once
        for rev in reviewers:
            for req in random.sample(reqs, random.randint(30,40)):
                FundingReviewFactory(score=random.randint(-2,2), funding=req, reviewer=rev)
        db_session.commit()

        do_login(app, reviewers[0])
        resp = app.get(url_for(controller='funding', action='summary', id=None))
        body = unicode(resp.body, 'utf-8')
        tables = BeautifulSoup(resp.body).findAll('table')
        assert len(tables) == len(types)

        assert "Application Funding Review Summary" in body

    def test_delete(self):
        pass # No delete function
