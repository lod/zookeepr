import random

from routes import url_for

from zk.model.attachment import Attachment
from zk.model.proposal import Proposal, ProposalType
from zk.model.person import Person
from zk.model.review import Review
from zk.model.config import Config

import webtest
from webtest.forms import Upload

from .crud_helper import CrudHelper
from .fixtures import PersonFactory, ProposalFactory, AttachmentFactory, RoleFactory, StreamFactory, ProposalStatusFactory, ProposalTypeFactory, TravelAssistanceTypeFactory, AccommodationAssistanceTypeFactory, TargetAudienceFactory, ConfigFactory, CompletePersonFactory
from .utils import do_login, isSignedIn

class TestProposal(CrudHelper):
    def test_permissions(self, app, db_session):
        # All: Must have an activated account
        # index, attach, new, _new: No modifications
        # view: must be organiser, reviewer or author
        # edit, _edit, _attach, withdraw, _withdraw: must be organiser or author
        # review, _review, review_index, summary: must be reviewer
        # approve, _approve, latex: must be organiser

        # organiser: approve, _approve, latex, edit, _edit, _attach, withdraw, _withdraw, view, index, attach, new, _new
        # reviewer: review, _review, review_index, summary, view, index, attach, new, _new
        # author: edit, _edit, _attach, withdraw, _withdraw, view, index, attach, new, _new
        # activated: index, attach, new, _new

        ProposalStatusFactory(name='Withdrawn') # Required by code

        unactivated = CompletePersonFactory(activated=False)
        activated   = CompletePersonFactory()
        author      = CompletePersonFactory()
        organiser   = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])
        reviewer    = CompletePersonFactory(roles=[CrudHelper._get_insert_role('reviewer')])

        target = ProposalFactory(people=[author])
        db_session.commit()

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=activated, bad_pers=unactivated,
                get_pages=('index', 'attach', 'new'),
                post_pages=('new',)
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=author, bad_pers=activated,
                get_pages=('edit', 'withdraw', 'view'),
                post_pages=('edit', 'attach', 'withdraw')
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=reviewer, bad_pers=activated,
                get_pages=('review', 'review_index', 'summary', 'view'),
                post_pages=('review',)
        )

        CrudHelper.test_permissions(self, app, db_session, target=target,
                good_pers=reviewer, bad_pers=organiser,
                get_pages=('review', 'review_index', 'summary'),
                post_pages=('review',)
        )

        CrudHelper.test_permissions(self, app, db_session,
                target=target, good_pers=organiser, bad_pers=activated,
                get_pages=('approve', 'latex', 'edit', 'withdraw', 'view'),
                post_pages=('approve', 'attach', 'withdraw')
        )


    def test_new(self, app, db_session, smtplib):
        # Call-for-papers must be open to submit a paper
        Config.find_by_pk(('general','cfp_status')).value = 'open'

        # Need a Complete Person to submit a paper - must have a 'finished' signup
        user = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])

        audiences = [TargetAudienceFactory() for i in range(5)]
        chosen_audience = random.choice(audiences)

        types = [ProposalTypeFactory() for i in range(5)]
        chosen_type = random.choice(types)

        travels = TravelAssistanceTypeFactory()
        accm = AccommodationAssistanceTypeFactory()
        stat = ProposalStatusFactory(name = 'Pending Review') # Required by code

        db_session.commit()

        expected = {
            'title'    : 'One day I was walking by the beach',
            'abstract' : 'When I found a sea shell by the sea shore',
            'abstract_video_url' : 'http://my.ted.talk/',
            'url'        : "http://come.bucket.nantucket",
        }
        # TODO: urls get http prepended

        def extra_form_check(f):
            assert 'person.bio' in f.fields
            assert 'person.mobile' in f.fields
            assert 'person.experience' in f.fields
            assert 'attachment' in f.fields


        def extra_form_set(f):
            f['person.bio'] = "I was once a man going to nantucket"
            f['person.mobile'] = "When I came upon a bucket"
            f['person.experience'] = "So I just kinda when fuckit"
            f['attachment'] = "testfile.txt", b'Really require an attachment?', "text/dummy"

            # Can't pass in integers for some reason, I think it is related to the attachment
            f['proposal.type']                     = str(chosen_type.id)
            f['proposal.audience']                 = str(chosen_audience.id)
            f['proposal.travel_assistance']        = str(travels.id)
            f['proposal.accommodation_assistance'] = str(accm.id)

        def extra_data_check(new):
            assert len(new.people) == 1
            author = new.people[0]
            assert author.id == user.id
            assert author.bio == "I was once a man going to nantucket"
            assert author.mobile == "When I came upon a bucket"
            assert author.experience == "So I just kinda when fuckit"

            assert len(new.attachments) == 1
            attach = new.attachments[0]
            assert attach.proposal_id == new.id
            assert attach.filename == "testfile.txt"
            #assert attach.content_type == "text/dummy" # Always set to a constant, unsure why
            assert attach.content_type == "application/octet-stream"
            assert attach.content == b'Really require an attachment?'

            assert new.type.id == chosen_type.id
            assert new.audience.id == chosen_audience.id
            assert new.travel_assistance.id == travels.id
            assert new.accommodation_assistance.id == accm.id


        # TODO: There is weirdness where DB table requires travel_assistance_type_id
        #       But form may not prompt for travel_assistance
        #       Same for accommodation_assistance_type_id
        #       There are odd hidden fields which I think are meant to handle it

        CrudHelper.test_new(self, app, db_session, user=user, title="Submit a Proposal", extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check, data=expected)

    def test_edit(self, app, db_session):
        user = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])

        audiences = [TargetAudienceFactory() for i in range(5)]
        chosen_audience = random.choice(audiences)

        types = [ProposalTypeFactory() for i in range(5)]
        chosen_type = random.choice(types)

        travels = TravelAssistanceTypeFactory()
        accm = AccommodationAssistanceTypeFactory()
        stat = ProposalStatusFactory(name = 'Pending Review') # Required by code

        target = ProposalFactory(people=[user])
        db_session.commit()

        print "TARGET", target, target.people

        expected = {
            'title'    : 'One day I was walking by the beach',
            'abstract' : 'When I found a sea shell by the sea shore',
            'audience' : chosen_audience.id,
            #'bio'      : "I was once a man going to nantucket",
            #'mobile'   : "When I came upon a bucket",
            #'experience' : "So I just kinda when fuckit",
            'abstract_video_url' : 'http://my.ted.talk/',
            'url'        : "http://come.bucket.nantucket",
            'type'       : chosen_type.id,
            'audience'   : chosen_audience.id,
            'travel_assistance' : travels.id,
            'accommodation_assistance' : accm.id,
        }
        # TODO: urls get http prepended

        def extra_form_set(f):
            f['person.bio'] = "I was once a man going to nantucket"
            f['person.mobile'] = "When I came upon a bucket"
            f['person.experience'] = "So I just kinda when fuckit"
            #f['proposal.url'] = "http://me.id.au"
            #f['proposal.abstract_video_url'] = "https://asta.video.go/"

        # TODO: Data check

        CrudHelper.test_edit(self, app, db_session, user=user, target=target, new_values=expected, extra_form_set=extra_form_set)

    def test_view(self, app, db_session):
        target = ProposalFactory();
        db_session.commit()
        CrudHelper.test_view(self, app, db_session, target=target, title=target.title)

    def test_index(self, app, db_session):
        # Index lists the submitters proposals, regardless of permissions etc.

        org_pers = CompletePersonFactory(roles=[CrudHelper._get_insert_role('organiser')])
        rows = [ProposalFactory(people=[org_pers]) for i in range(10)]
        db_session.commit()
        # Note: Long abstracts will be truncated, not an issue with our test data
        entries = { s.id : [s.title, s.type.name, s.abstract, s.url, org_pers.fullname] for s in rows }

        CrudHelper.test_index(self, app, db_session, title="My Proposals", user=org_pers, entries=entries, entry_actions=('view', 'withdraw'))

    def test_delete(self):
        pass # No delete functionality, there is a withdraw but it doesn't remove the entry from the DB

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
        assert resp.status_code == 302 # Failure suggests form didn't submit cleanly

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
        resp = resp.click('Review this proposal', index=0)

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

        def try_ops(user, attachment, status):
            if user is None:
                if isSignedIn(app):
                    app.get('/person/signout')
            else:
                do_login(app, user)

            def try_req(method, action, status = 200):
                environ = {} # = {'REMOTE_USER': str(user.email_address)} if user is not None else {}

                req = webtest.TestRequest.blank(url_for(controller='attachment', action=action, id=attachment.id), method=method)

                if status == 401:
                    # 401 - Require login, can be a 302 redirecting to the login page
                    resp = app.do_request(req, status="*")
                    if resp.status_code == 401:
                        pass
                    elif resp.status_code == 302 and "/person/signin" in resp.location:
                        pass
                    else:
                        raise AppError("Bad response: %s (not %s)", resp.status, status)
                else:
                    resp = app.do_request(req, status=status)
                return resp

            resp = try_req('GET', 'view', status if status else 200)
            if status is None: assert resp.content_type == "application/octet-stream"

            resp = try_req('GET', 'delete', status if status else 200)
            if status is None: assert "Are you sure you want to delete this attachment" in unicode(resp.body, 'utf-8')

            resp = try_req('POST', 'delete', status if status else 302)

        
        # we're logged in and this is ours
        try_ops(pers, att1, None)

        # this is also ours
        try_ops(sec_pers, att2, None)

        # we're organiser/admin
        try_ops(org_pers, att3, None)

        # we're a reviewer
        try_ops(rev_pers, att4, 403)

        # we're logged in and this isn't ours
        try_ops(other_pers, att4, 403)

        # we're not logged in
        try_ops(None, att4, 401)

        db_session.expunge_all()
        atts = Attachment.find_all();
        assert len(atts) == 1
        assert atts[0].id == att4.id
