from routes import url_for

from zk.model.attachment import Attachment
from zk.model.proposal import Proposal, ProposalType
from zk.model.person import Person
from zk.model.review import Review

from webtest.forms import Upload

from .fixtures import PersonFactory, ProposalFactory, AttachmentFactory, RoleFactory, StreamFactory, ProposalStatusFactory, ProposalTypeFactory, TravelAssistanceTypeFactory, AccommodationAssistanceTypeFactory, TargetAudienceFactory, ConfigFactory, CompletePersonFactory
from .utils import do_login, isSignedIn, TableParser

class TestProposal(object):

    def test_proposal_view_lockdown(self, app, db_session):
        prop = ProposalFactory()
        pers1 = PersonFactory(proposals = [prop])
        pers2 = PersonFactory()
        db_session.commit()

        # try to view the proposal as the other person
        do_login(app, pers2)
        resp = app.get(url_for(controller='proposal', action='edit', id=prop.id), status=403)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id), status=403)


    def test_proposal_edit_lockdown(self, app, db_session):
        prop = ProposalFactory()
        pers1 = PersonFactory(proposals = [prop])
        pers2 = PersonFactory()
        db_session.commit()

        # try to edit the proposal as the other person
        do_login(app, pers2)
        resp = app.get(url_for(controller='proposal', action='edit', id=prop.id), status=403)
        resp = app.post(url_for(controller='proposal', action='edit', id=prop.id), params={}, status=403)


    def test_proposal_withdraw_lockdown(self, app, db_session):
        prop = ProposalFactory()
        pers1 = PersonFactory(proposals = [prop])
        pers2 = PersonFactory()
        db_session.commit()

        # try to delete the proposal as the other person
        do_login(app, pers2)
        resp = app.get(url_for(controller='proposal', action='withdraw', id=prop.id), status=403)
        resp = app.post(url_for(controller='proposal', action='withdraw', id=prop.id), params={}, status=403)

    def test_proposal_list_lockdown(self, app, db_session):
        prop = ProposalFactory()
        pers1 = PersonFactory(proposals = [prop])
        pers2 = PersonFactory()
        db_session.commit()

        # try to view the proposal as the other person
        do_login(app, pers2)
        resp = app.get(url_for(controller='proposal', action='index'))
        assert prop.title not in unicode(resp.body, 'utf-8')
        assert "You haven't submitted any proposals" in unicode(resp.body, 'utf-8')

    def test_submit_another(self, app, db_session, smtplib):
        # created guy and proposal
        pers = CompletePersonFactory()
        prop = ProposalFactory(title='sub one', people=[pers])
        type = ProposalTypeFactory()
        stat = ProposalStatusFactory(name = 'Pending Review') # Required by code
        trav = TravelAssistanceTypeFactory()
        accm = AccommodationAssistanceTypeFactory()
        audc = TargetAudienceFactory()
        db_session.commit()

        # now go to list, click on the submit another link, and do so
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='index'))
        assert prop.title in unicode(resp.body, 'utf-8')
        assert "You haven't submitted any proposals" not in unicode(resp.body, 'utf-8')

        resp = resp.click(description='New proposal')
        resp = resp.maybe_follow()
        f = resp.form
        f['proposal.title']    = 'sub two'
        f['proposal.type']     = str(type.id)
        f['proposal.abstract'] = "cubist"
        f['proposal.accommodation_assistance'] = str(accm.id)
        f['proposal.travel_assistance'] = str(trav.id)
        f['proposal.audience'] = str(audc.id)
        f['person.experience'] = "n"
        f['attachment']        = "foo"
        f['person.mobile']     = "NONE"
        f['person.bio']        = "Jim isn't real Dave, he never was"
        resp = f.submit()
        resp.status_code = 302 # Failure suggests form didn't submit cleanly

        pers_id = pers.id
        db_session.expunge_all()

        # does it exist?
        s2 = Proposal.find_by_title('sub two')
        assert len(s2) == 1
        s2 = s2[0]
        assert Person.find_by_id(pers_id) in s2.people # Attached to correct person
        assert len(s2.attachments) == 1 # With attachment

        # Ensure that confirmation email was sent
        assert smtplib.existing is not None
        assert "Thank you for proposing" in smtplib.existing.message

    def test_proposal_list_normals_denied(self, app, db_session):
        pers = PersonFactory()
        prop = ProposalFactory()
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        # we're logged in but still can't see it
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='review_index'), status=403)

    def test_proposal_list_reviewer(self, app, db_session):
        role = RoleFactory(name = 'reviewer')
        pers = PersonFactory(roles = [role])
        prop = ProposalFactory()
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        # we're logged in and we're a reviewer
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='review_index'))

    def test_proposal_view(self, app, db_session):
        pers = PersonFactory()
        prop = ProposalFactory()
        db_session.commit()
        
        # we're logged in but this isn't our proposal..
        # should 403
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id), status=403)
                            
    def test_proposal_view_ours(self, app, db_session):
        prop = ProposalFactory()
        pers = PersonFactory(proposals = [prop])
        db_session.commit()
        
        # we're logged in and this is ours
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))

    def test_proposal_view_as_reviewer(self, app, db_session):
        prop = ProposalFactory()
        role = RoleFactory(name = 'reviewer')
        pers = PersonFactory(roles = [role])
        strm = StreamFactory() # need a stream
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        do_login(app, pers)

        # reviewers can review a proposal
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))

        # get the form and start reviewing!
        f = resp.form
        f['review.score'] = 1
        f['review.stream'] = strm.id
        f['review.comment'] = "snuh"
        f.submit()

        db_session.expunge_all()

        # test that we have a review
        reviews = Review.find_all()
        assert len(reviews) == 1
        assert reviews[0].comment == "snuh"
                                                            
        
    def test_proposal_attach_more(self, app, db_session):
        pers = PersonFactory()
        prop = ProposalFactory(people = [pers])
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()
        
        # we're logged in and this is ours
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        resp = resp.click('Add an attachment')

        f = resp.form
        f['attachment'] = Upload("test.ini")
        resp = f.submit()
        resp = resp.follow()

        db_session.expunge_all()

        atts = Attachment.find_all();
        assert len(atts) == 1
        assert '[app:main]' in atts[0].content

        
    def test_proposal_delete_attachment(self, app, db_session):
        pers = PersonFactory()
        prop = ProposalFactory()
        pers.proposals.append(prop)
        atta = AttachmentFactory(proposal=prop)
        db_session.commit()
        
        # we're logged in and this is ours
        do_login(app, pers)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        resp = resp.click('delete')

        f = resp.form
        resp = f.submit()

        resp = resp.follow()

        assert resp.request.path == url_for(controller='proposal', action='view', id=prop.id)

        db_session.expunge_all()

        atts = Attachment.find_all();
        assert atts == []

    def test_view_proposal_permissions(self, app, db_session):
        # Rules - people with the following conditions can view a proposal:
        #   The person who submitted the proposal
        #   An organiser
        #   A reviewer
        # The following can edit a proposal (get an edit proposal link):
        #   The person who submitted the proposal if proposal_editing is open
        #   The person who submitted the proposal if they have the late submitter role
        #   An organiser
        # The following can review a proposal (get review form):
        #   A reviewer

        organiser_role = RoleFactory(name = 'organiser')
        reviewer_role  = RoleFactory(name = 'reviewer')
        late_role      = RoleFactory(name = 'late_submitter')

        joe_public     = CompletePersonFactory()
        submitter      = CompletePersonFactory()
        late_submitter = CompletePersonFactory(roles=[late_role])
        organiser      = CompletePersonFactory(roles=[organiser_role])
        reviewer       = CompletePersonFactory(roles=[reviewer_role])
        super_reviewer = CompletePersonFactory(roles=[organiser_role, reviewer_role])
        prop = ProposalFactory(people=[submitter,late_submitter])

        ProposalStatusFactory(name='Withdrawn') # Required by code
        ConfigFactory(key='proposal_editing', value='open')
        db_session.commit()

        # Not logged in can't access the page, prompted to log in
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        resp = resp.maybe_follow()
        assert "enter your credentials in the following form" in unicode(resp.body, 'utf-8')

        # Joe public can't access the page, denied
        do_login(app, joe_public)
        app.get(url_for(controller='proposal', action='view', id=prop.id), status=403)

        # Submitter, can view, edit, not review, not stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, submitter)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" not in unicode(resp.body, 'utf-8')

        # Late submitter, can view, edit, not review, not stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, late_submitter)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" not in unicode(resp.body, 'utf-8')

        # Organiser, can view, edit, not review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, organiser)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

        # Reviewer, can view, not edit, review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, reviewer)
        assert isSignedIn(app)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" not in unicode(resp.body, 'utf-8')
        assert "Proposal Review" in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

        # Super reviewer, can view, edit, review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, super_reviewer)
        assert isSignedIn(app)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

        Config.find_by_pk(('general','proposal_editing')).value = 'closed'
        db_session.commit()

        # Not logged in can't access the page, prompted to log in
        app.get(url_for(controller='person', action='signout', id=None))
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        resp = resp.maybe_follow()
        assert "enter your credentials in the following form" in unicode(resp.body, 'utf-8')

        # Joe public can't access the page, denied
        do_login(app, joe_public)
        app.get(url_for(controller='proposal', action='view', id=prop.id), status=403)

        # Submitter, can view, not edit, not review, not stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, submitter)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" not in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" not in unicode(resp.body, 'utf-8')

        # Late submitter, can view, edit, not review, not stalk
        app.get(url_for(controller='person', action='signout', id=None))
        assert not isSignedIn(app)
        do_login(app, late_submitter)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" not in unicode(resp.body, 'utf-8')

        # Organiser, can view, edit, not review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, organiser)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" not in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

        # Reviewer, can view, not edit, review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, reviewer)
        assert isSignedIn(app)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" not in unicode(resp.body, 'utf-8')
        assert "Proposal Review" in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

        # Super reviewer, can view, edit, review, stalk
        app.get(url_for(controller='person', action='signout', id=None))
        do_login(app, super_reviewer)
        assert isSignedIn(app)
        resp = app.get(url_for(controller='proposal', action='view', id=prop.id))
        assert "Proposal for" in unicode(resp.body, 'utf-8')
        assert "Edit Proposal" in unicode(resp.body, 'utf-8')
        assert "Proposal Review" in unicode(resp.body, 'utf-8')
        assert "stalk on Google" in unicode(resp.body, 'utf-8')

    def test_approve(self, app, db_session):
        """ Giant list of talks allows changing status/approval """

        organiser = CompletePersonFactory(roles=[RoleFactory(name = 'organiser')])
        t1 = ProposalTypeFactory()
        t2 = ProposalTypeFactory()
        t3 = ProposalTypeFactory()

        for i in range(5):
            ProposalFactory(type=t2)
        for i in range(5):
            ProposalFactory(type=t3)
        for i in range(5):
            ProposalFactory(type=t1)
        for i in range(5):
            ProposalFactory(type=t2)

        db_session.commit()
        do_login(app, organiser)
        resp = app.get(url_for(controller='proposal', action='approve'))

        parser = TableParser()
        parser.feed(resp.body)

        # Table for each Proposal Type
        assert len(parser.tables) == 3

# TODO: Test for when proposal_editing is closed/open/not_open


from zk.model.config import Config

class TestCFPStates(object):

    def test_not_open(self, app, db_session):
        # Entry created by init, update it
        Config.find_by_pk(('general','cfp_status')).value = 'not_open'
        pers = CompletePersonFactory()
        db_session.commit()

        resp = do_login(app, pers)
        resp = app.get('/programme/submit_a_proposal')
        assert "The call for proposals has not opened yet" in unicode(resp.body, 'utf-8')

    def test_open(self, app, db_session):
        # Entry created by init, update it
        Config.find_by_pk(('general','cfp_status')).value = 'open'
        pers = CompletePersonFactory()
        db_session.commit()

        resp = do_login(app, pers)
        resp = app.get('/programme/submit_a_proposal')
        assert "The name of your proposal" in unicode(resp.body, 'utf-8')

    def test_closed(self, app, db_session):
        # Entry created by init, update it
        Config.find_by_pk(('general','cfp_status')).value = 'closed'
        pers = CompletePersonFactory()
        db_session.commit()

        resp = do_login(app, pers)
        resp = app.get('/programme/submit_a_proposal')
        assert "The call for proposals is now closed" in unicode(resp.body, 'utf-8')

class TestAttachment(object):

    def test_permissions(self, app, db_session):
        pers = PersonFactory()
        sec_pers = PersonFactory()
        rev_pers = PersonFactory(roles = [RoleFactory(name = 'reviewer')])
        org_pers = PersonFactory(roles = [RoleFactory(name = 'organiser')])
        other_pers = PersonFactory()
        ProposalStatusFactory(name='Withdrawn') # Required by code
        # Multiple attachments for deletion testing
        prop = ProposalFactory(people = [pers, sec_pers])
        att1 = AttachmentFactory(proposal=prop)
        att2 = AttachmentFactory(proposal=prop)
        att3 = AttachmentFactory(proposal=prop)
        att4 = AttachmentFactory(proposal=prop)
        db_session.commit()
        
        # we're logged in and this is ours
        do_login(app, pers)
        resp = app.get(url_for(controller='attachment', action='view', id=att1.id))
        assert resp.content_type == "application/octet-stream"
        resp = app.get(url_for(controller='attachment', action='delete', id=att1.id))
        assert "Are you sure you want to delete this attachment" in unicode(resp.body, 'utf-8')
        resp = app.post(url_for(controller='attachment', action='delete', id=att1.id), status=302)

        # this is also ours
        do_login(app, sec_pers)
        resp = app.get(url_for(controller='attachment', action='view', id=att2.id))
        assert resp.content_type == "application/octet-stream"
        resp = app.get(url_for(controller='attachment', action='delete', id=att2.id))
        assert "Are you sure you want to delete this attachment" in unicode(resp.body, 'utf-8')
        resp = app.post(url_for(controller='attachment', action='delete', id=att2.id), status=302)

        # we're organiser/admin
        do_login(app, org_pers)
        resp = app.get(url_for(controller='attachment', action='view', id=att3.id))
        assert resp.content_type == "application/octet-stream"
        resp = app.get(url_for(controller='attachment', action='delete', id=att3.id))
        assert "Are you sure you want to delete this attachment" in unicode(resp.body, 'utf-8')
        resp = app.post(url_for(controller='attachment', action='delete', id=att3.id), status=302)

        # we're a reviewer
        do_login(app, rev_pers)
        resp = app.get(url_for(controller='attachment', action='view', id=att4.id), status=403)
        assert resp.content_type == "text/html"
        resp = app.get(url_for(controller='attachment', action='delete', id=att4.id), status=403)
        resp = app.post(url_for(controller='attachment', action='delete', id=att4.id), status=403)

        # we're logged in and this isn't ours
        do_login(app, other_pers)
        resp = app.get(url_for(controller='attachment', action='view', id=att4.id), status=403)
        assert resp.content_type == "text/html"
        resp = app.get(url_for(controller='attachment', action='delete', id=att4.id), status=403)
        resp = app.post(url_for(controller='attachment', action='delete', id=att4.id), status=403)

        # we're not logged in
        app.get('/person/signout')
        assert not isSignedIn(app)
        resp = app.get(url_for(controller='attachment', action='view', id=att4.id))#, status=404)
        assert resp.content_type == "text/html"
        assert "User doesn't have any of the specified roles" in unicode(resp.body, 'utf-8')
        resp = app.get(url_for(controller='attachment', action='delete', id=att4.id))
        assert "Don't have an account?" in unicode(resp.body, 'utf-8')
        resp = app.post(url_for(controller='attachment', action='delete', id=att4.id))
        assert "Don't have an account?" in unicode(resp.body, 'utf-8')

        db_session.expunge_all()
        atts = Attachment.find_all();
        assert len(atts) == 1
        assert atts[0].id == att4.id
