import pytest
from routes import url_for

from zk.model.review import Review

from .fixtures import StreamFactory, PersonFactory, ProposalFactory, RoleFactory, ProposalStatusFactory, ReviewFactory, CompletePersonFactory
from .utils import do_login, TableParser


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

        p1 = PersonFactory(roles=[RoleFactory(name='reviewer')], firstname="Scrouge", lastname="McHouse")
        p2 = PersonFactory(firstname="Daffy", lastname="Laffy")
        p3 = PersonFactory()
        prop = ProposalFactory(people=[p3])
        stream = StreamFactory()
        r1 = ReviewFactory(reviewer=p1, proposal=prop, score=-1, stream=stream)
        r2 = ReviewFactory(reviewer=p2, proposal=prop, score=2, stream=stream)
        ProposalStatusFactory(name='Withdrawn') # Required by code
        db_session.commit()

        do_login(app, p1)
        resp = app.get('/proposal/%d' % prop.id)
        print resp

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
        for i in range(6):
            assert len(table[i]) == 3


        # Chair can see average scores
        do_login(app, chair)
        resp = app.get(url_for(controller='review', action='summary'))
        parser = TableParser()
        parser.feed(resp.body)
        chair_table = parser.tables[0]

        # Table should be the same except for the extra column
        assert len(chair_table) == 6 # Five reviewers + heading
        for i in range(6):
            assert chair_table[i][0:3] == table[i][0:3]

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

    def test_duplicate_proposal(self, app, db_session):
        """ Reviewers should be alerted to potential duplicate submissions. """

        ProposalStatusFactory(name='Withdrawn') # Required by code

        p1 = CompletePersonFactory()
        p2 = CompletePersonFactory()
        p3 = CompletePersonFactory()

        base_title = "An identical title discussing some detail"
        similar_title = "An identical title discussing some details"
        dissimilar_title = "A dissimilar title conversing on a beach"

        base_abstract = """
            Bacon ipsum dolor amet kielbasa chicken beef spare ribs, landjaeger jerky chuck boudin ground round shankle venison ribeye sirloin cow tenderloin. T-bone drumstick tongue fatback rump alcatra. Ribeye filet mignon pork chuck brisket corned beef t-bone. Kielbasa bresaola swine porchetta alcatra ground round brisket capicola cupim. Porchetta spare ribs drumstick, pork belly andouille jowl alcatra rump pancetta. Boudin swine meatloaf turducken frankfurter pastrami cow filet mignon bacon andouille landjaeger kevin. Rump pancetta drumstick kielbasa, boudin frankfurter flank bresaola prosciutto tongue filet mignon.

            Filet mignon boudin pork salami ribeye drumstick. Capicola jerky bacon, beef pastrami short ribs porchetta. Bresaola bacon t-bone pork chop meatloaf cow. Ground round shankle tongue, salami shoulder tail jowl tenderloin sausage venison. Brisket shoulder beef porchetta kielbasa. Ground round short ribs swine tail meatloaf landjaeger rump pig cow kielbasa. Shank landjaeger pork meatball kielbasa.
            """
        dissimilar_abstract = """
            Turnip greens yarrow ricebean rutabaga endive cauliflower sea lettuce kohlrabi amaranth water spinach avocado daikon napa cabbage asparagus winter purslane kale. Celery potato scallion desert raisin horseradish spinach carrot soko. Lotus root water spinach fennel kombu maize bamboo shoot green bean swiss chard seakale pumpkin onion chickpea gram corn pea. Brussels sprout coriander water chestnut gourd swiss chard wakame kohlrabi beetroot carrot watercress. Corn amaranth salsify bunya nuts nori azuki bean chickweed potato bell pepper artichoke. 
            """
        similar_abstract = base_abstract.replace("drumstick", "child meat")
        similar_abstract = similar_abstract.replace("pork", "holy")

        base                = ProposalFactory(people=[p1], title=base_title, abstract=base_abstract)
        duplicate_title     = ProposalFactory(people=[p2], title=base_title)
        similar_title       = ProposalFactory(people=[p1,p2,p3], title=similar_title)
        duplicate_abstract  = ProposalFactory(people=[p3], abstract=base_abstract)
        similar_abstract    = ProposalFactory(people=[p2,p1], abstract=similar_abstract)
        dissimilar          = ProposalFactory(people=[p3], title=dissimilar_title, abstract=dissimilar_abstract)

        pers = PersonFactory(roles=[RoleFactory(name='reviewer')])

        db_session.commit()

        do_login(app, pers)

        resp = app.get('/proposal/%d/view' % base.id)

        parser = TableParser(id="duplicates")
        parser.feed(resp.body)
        dup_table = parser.tables[0]

        assert len(dup_table) == 5 # 2 title dups + 2 abstract dups + heading
        # Each table row is (people, title)
        titles = [dup_table[i][1] for i in range(1,5)]
        for test_dup in [duplicate_title, similar_title, duplicate_abstract, similar_abstract]:
            assert test_dup.title in titles
            assert dup_table[titles.index(test_dup.title)+1][0] == ", ".join([x.fullname for x in test_dup.people])

        # No duplicates -> no table
        resp = app.get('/proposal/%d/view' % dissimilar.id)
        parser = TableParser(id="duplicates")
        parser.feed(resp.body)
        assert parser.tables == []

