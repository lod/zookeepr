import pytest
from routes import url_for

from HTMLParser import HTMLParser

from zk.model.review import Review

from .fixtures import StreamFactory, PersonFactory, ProposalFactory, RoleFactory, ProposalStatusFactory, ReviewFactory, CompletePersonFactory
from .utils import do_login

class TableParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs) # Old style class
        self.tables = []
        self.in_cell = False
    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        if tag == "tr":
            self.tables[-1].append([])
        if tag == "td" or tag == "th":
            self.in_cell = True
            self.tables[-1][-1].append("")
    def handle_endtag(self, tag):
        if tag == "td" or tag == "th":
            self.in_cell = False
    def handle_data(self, data):
        if self.in_cell:
            self.tables[-1][-1][-1] += data



class TestReviewController(object):

    def test_create(self, app, db_session):

        StreamFactory(name='streamy')
        prop1 = ProposalFactory()
        prop2 = ProposalFactory()
        p = PersonFactory(roles=[RoleFactory(name='reviewer')])

        ProposalStatusFactory(name='Withdrawn') # Required by code


        db_session.commit()

        do_login(app, p)

        resp = app.get('/proposal/%d/view' % prop1.id)
        resp = resp.maybe_follow()
        f = resp.form
        f['review.score'] = -1
        f['review.comment'] = 'a'
        resp = f.submit()
        resp = resp.follow() # Failure indicates form validation error

        resp = app.get('/proposal/%d/view' % prop2.id)
        resp = resp.maybe_follow()
        f = resp.form
        f['review.score'] = 2
        f['review.comment'] = 'b'
        resp = f.submit()
        resp = resp.follow() # Failure indicates form validation error

        db_session.expunge_all()

        revs = Review.find_all()
        assert len(revs) == 2
        assert revs[0].score == -1
        assert revs[0].comment == 'a'
        assert revs[1].score == 2
        assert revs[1].comment == 'b'


    @pytest.mark.xfail # Test not yet written
    def test_review_feedback(self):
        """Test that one can put in optional feedback to the submitter from the review interface.
        """
        assert False

    @pytest.mark.xfail # Test not yet written
    def test_review_interface(self):
        """Test that the interface shows two lists, one of unreviewed proposals, and one of reviewed proposals"""
        assert False


    @pytest.mark.xfail # Test not yet written
    def test_review_interface_sorted(self):
        """Test that the reviewed proposals are sorted by rank"""
        assert False


    def test_reviews_not_isolated(self, app, db_session):
        """Test that a reviewer can see other reviews"""

        p1 = PersonFactory(roles=[RoleFactory(name='reviewer')], firstname="Scrouge")
        p2 = PersonFactory(firstname="Daffy")
        p3 = PersonFactory()
        prop = ProposalFactory(people=[p3])
        stream = StreamFactory()
        r1 = ReviewFactory(reviewer=p1, proposal=prop, score=-1, stream=stream)
        r2 = ReviewFactory(reviewer=p2, proposal=prop, score=2, stream=stream)
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        do_login(app, p1)
        resp = app.get('/proposal/%d' % prop.id)

        # Page has list of reviews already set on proposal
        assert p1.firstname in unicode(resp.body, 'utf-8')
        assert p2.firstname in unicode(resp.body, 'utf-8')


    @pytest.mark.xfail # Test not yet written
    def test_reviewer_name_hidden_from_submitter(self):
        """Test that a reviewer is anonymouse to submitters"""
        assert False


    @pytest.mark.xfail # Test not yet written
    def test_reviewer_cant_review_own_proposal(self):
        """Test that a reviewer can't review their own submissions."""
        assert False


    def test_only_one_review_per_reviewer_per_proposal(self, app, db_session):
        """test that reviewers can only do one review per proposal"""

        p1 = PersonFactory(roles=[RoleFactory(name='reviewer')])
        p2 = PersonFactory()
        prop = ProposalFactory(people=[p2])
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        do_login(app, p1)
        resp = app.get('/proposal/%d/view' % prop.id)
        f = resp.form
        f['review.comment'] = 'first_review_comment'
        resp = f.submit()

        # do it again 
        f['review.comment'] = 'second_review_comment'
        resp = f.submit()
        resp = resp.follow() # Failure linked to errors in form submission

        # Old behaviour alerted that review had been performed
        # New behaviour is that we simply update with the second result

        db_session.expunge_all()

        revs = Review.find_all()
        assert len(revs) == 1
        assert revs[0].comment == "second_review_comment"


        # TODO: Test Config cfp_miniconf_list, should be used to populate list, when empty section should be hidden
        #       Maybe - Verification should ensure that added value is on list
        #       Maybe - Use DB?
        #       Same for stream, db table stream

        # TODO: Review editing should not show skip option, maybe keep or reset?
        
    def test_edit_review(self, app, db_session):
        """test that a reviewer can edit their review"""

        s1 = StreamFactory(name='Here he comes')
        s2 = StreamFactory(name='here comes speedracer')
        s3 = StreamFactory(name='He\'s a demon on wheels')

        p1 = PersonFactory(roles=[RoleFactory(name='reviewer')])
        p2 = PersonFactory()
        prop = ProposalFactory(people=[p2])
        r = ReviewFactory(proposal=prop, reviewer=p1, score=-2, comment="It's a hard luck life", miniconf="Worshipping lod", stream=s2)
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        do_login(app, p1)
        resp = app.get(url_for(controller='review', action='edit', id=r.id))
        resp = resp.maybe_follow()
        assert r.comment in unicode(resp.body, 'utf-8')
        f = resp.form

        # Ensure existing values are populating form
        assert f['review.score'].value, r.score
        assert f['review.miniconf'].value, r.miniconf
        assert f['review.stream'].value, r.stream.id
        assert f['review.comment'].value, r.comment
        assert f['review.private_comment'].value, r.private_comment

        f['review.comment'] = 'hi!'
        f['review.score'] = 1
        f['review.miniconf'] = "bow before him"
        f['review.stream'] = s3.id

        resp = f.submit()
        resp = resp.follow()

        rid = r.id
        sid = s3.id
        db_session.expunge_all()
        r2 = Review.find_by_id(rid)

        assert r2.comment == 'hi!'
        assert r2.score   == 1
        assert r2.stream_id == sid
        assert r2.miniconf == "bow before him"

    def test_reviewer_summary(self, app, db_session):
        """ Test display of /review/summary page """

        r_reviewer = RoleFactory(name='reviewer')
        reviewer = CompletePersonFactory(roles=[r_reviewer])
        chair = CompletePersonFactory(roles=[RoleFactory(name='proposals_chair')])
        organiser = CompletePersonFactory(roles=[RoleFactory(name='organiser')])

        # Using complete people to get names
        r2 = CompletePersonFactory(roles=[r_reviewer])
        r3 = CompletePersonFactory(roles=[r_reviewer])
        r4 = CompletePersonFactory(roles=[r_reviewer])
        r5 = CompletePersonFactory(roles=[r_reviewer])

        ReviewFactory(reviewer=reviewer, score=1)
        ReviewFactory(reviewer=reviewer, score=2)
        ReviewFactory(reviewer=reviewer, score=3)
        ReviewFactory(reviewer=reviewer, score=4)
        ReviewFactory(reviewer=reviewer, score=5)
        # Average = 15/5 = 3.00

        ReviewFactory(reviewer=r2, score=0)
        ReviewFactory(reviewer=r2, score=-5)
        ReviewFactory(reviewer=r2, score=-3)
        ReviewFactory(reviewer=r2, score=6)
        ReviewFactory(reviewer=r2, score=2)
        # Average = 0/5 = 0.00

        ReviewFactory(reviewer=r3, score=None)
        ReviewFactory(reviewer=r3, score=None)
        ReviewFactory(reviewer=r3, score=None)
        # Average = None

        ReviewFactory(reviewer=r4, score=0)
        ReviewFactory(reviewer=r4, score=None)
        ReviewFactory(reviewer=r4, score=-3)
        ReviewFactory(reviewer=r4, score=-6)
        ReviewFactory(reviewer=r4, score=2)
        ReviewFactory(reviewer=r4, score=5)
        ReviewFactory(reviewer=r4, score=-11)
        # Average = -13/6 = 2.1666

        # r5 has no reviews

        db_session.commit()

        do_login(app, reviewer)
        resp = app.get(url_for(controller='review', action='summary'))
        parser = TableParser()
        parser.feed(resp.body)
        table = parser.tables[0]

        assert len(table) == 6 # Five reviewers + heading

        assert table[1][0] == reviewer.fullname
        assert table[2][0] == r2.fullname
        assert table[3][0] == r3.fullname
        assert table[4][0] == r4.fullname
        assert table[5][0] == r5.fullname

        # Number of reviews
        assert table[1][1] == "5"
        assert table[2][1] == "5"
        assert table[3][1] == "0"
        assert table[4][1] == "6"
        assert table[5][1] == "0"

        # Number of declined reviews
        assert table[1][2] == "0"
        assert table[2][2] == "0"
        assert table[3][2] == "3"
        assert table[4][2] == "1"
        assert table[5][2] == "0"

        # Average score isn't visible
        assert len(table[0]) == 3
        assert len(table[1]) == 3
        assert len(table[2]) == 3
        assert len(table[3]) == 3
        assert len(table[4]) == 3
        assert len(table[5]) == 3


        # Chair can see average scores
        do_login(app, chair)
        resp = app.get(url_for(controller='review', action='summary'))
        parser = TableParser()
        parser.feed(resp.body)
        chair_table = parser.tables[0]

        # Table should be the same except for the extra column
        assert len(chair_table) == 6 # Five reviewers + heading
        assert chair_table[0][0:3] == table[0][0:3]
        assert chair_table[1][0:3] == table[1][0:3]
        assert chair_table[2][0:3] == table[2][0:3]
        assert chair_table[3][0:3] == table[3][0:3]
        assert chair_table[4][0:3] == table[4][0:3]
        assert chair_table[5][0:3] == table[5][0:3]

        # Average score
        assert chair_table[1][3] == "3.00"
        assert chair_table[2][3] == "0.00"
        assert chair_table[3][3] == "0.00"
        assert chair_table[4][3] == "-2.17"
        assert chair_table[5][3] == "0.00"

        # Organiser can also see average scores
        do_login(app, organiser)
        resp = app.get(url_for(controller='review', action='summary'))
        parser = TableParser()
        parser.feed(resp.body)
        assert parser.tables[0] == chair_table
