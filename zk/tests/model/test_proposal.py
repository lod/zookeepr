# pytest magic: from .conftest import app_config, db_session

from .fixtures import PersonFactory, ProposalFactory, ProposalTypeFactory, AttachmentFactory, ReviewFactory, ProposalStatusFactory, RoleFactory, ConfigFactory

from zk.model.proposal import Proposal, ProposalType
from zk.model.person import Person
from zk.model.attachment import Attachment
from zk.model.review import Review

import zk.model.meta as meta
import zkpylons.model.meta as pymeta
import random

class TestProposal(object):
    def test_create(self, db_session):
        person_id = 1
        proposal_type_id = 10
        proposal_id = 15

        proposal_type = ProposalTypeFactory(id=proposal_type_id)
        person = PersonFactory(id=person_id)
        proposal = ProposalFactory(id=proposal_id, type=proposal_type)
        db_session.flush()
        
        # give this sub to person
        person.proposals.append(proposal)
        db_session.flush()

        proposal_type = ProposalType.find_by_id(proposal_type_id)
        person = Person.find_by_id(person_id, abort_404=False)
        proposal = Proposal.find_by_id(proposal_id, abort_404=False)
        
        assert person is not None
        assert proposal_type is not None
        assert proposal is not None

        assert len(person.proposals) == 1
        assert proposal.title == person.proposals[0].title

        # check references
        assert person.proposals[0].people[0] == person
        assert person.proposals[0].type.name == proposal_type.name

        # check the proposal relations
        assert proposal.type.name == proposal_type.name
        assert proposal.people[0] == person

        # perform and check delete
        db_session.delete(proposal)
        db_session.delete(proposal_type)
        db_session.delete(person)
        
        assert ProposalType.find_by_id(proposal_type_id)         is None
        assert Person.find_by_id(person_id, abort_404=False)     is None
        assert Proposal.find_by_id(proposal_id, abort_404=False) is None


    def test_double_person_proposal_mapping(self, db_session):
        person1 = PersonFactory()
        person2 = PersonFactory()
        proposal1 = ProposalFactory()
        proposal2 = ProposalFactory()
        db_session.flush()

        person1.proposals.append(proposal1)
        person2.proposals.append(proposal2)
        db_session.flush()

        assert proposal1 in person1.proposals
        assert proposal2 in person2.proposals

        # Ensure proposals are only in matching preson
        assert proposal1 not in person2.proposals
        assert proposal2 not in person1.proposals


    def test_multiple_persons_per_proposal(self, db_session):
        person1 = PersonFactory()
        person2 = PersonFactory()
        person3 = PersonFactory()
        proposal = ProposalFactory()
        db_session.flush()

        person1.proposals.append(proposal)
        proposal.people.append(person2)
        db_session.flush()

        assert proposal in person1.proposals
        assert proposal in person2.proposals

        assert person1 in proposal.people
        assert person2 in proposal.people

        assert proposal not in person3.proposals
        assert person3 not in proposal.people


    def test_proposal_with_attachment(self, db_session):
        proposal = ProposalFactory()
        attachment = AttachmentFactory(proposal_id = proposal.id)
        db_session.flush()

        proposal.attachments.append(attachment)
        db_session.flush()

        proposal = Proposal.find_by_id(proposal.id)
        attachment = Attachment.find_by_id(attachment.id)
        assert proposal.attachments[0] == attachment

    def test_reviewed_proposal(self, db_session):
        person1  = PersonFactory()
        person2  = PersonFactory()
        proposal = ProposalFactory()
        review   = ReviewFactory(reviewer=person2)

        with meta.Session.no_autoflush:
            with pymeta.Session.no_autoflush:
                person1.proposals.append(proposal)
                proposal.reviews.append(review) # Must be done before flush
        db_session.flush()

        assert proposal in person1.proposals
        assert proposal not in person2.proposals

        assert person1 in proposal.people
        assert person2 not in proposal.people

        assert review in proposal.reviews

    def test_average_score(self, db_session):
        prop = ProposalFactory()
        r1   = ReviewFactory(proposal=prop, score=5)
        r2   = ReviewFactory(proposal=prop, score=-10)
        r3   = ReviewFactory(proposal=prop, score=23)
        r4   = ReviewFactory(proposal=prop, score=None)
        db_session.flush()

        # 5-10+23/3 == 18/3 == 6
        assert prop.average_score == 6

    def test_find_next_proposal(self, db_session):
        """ Find the next proposal for a reviewer to look at.
            Do not select a proposal that the reviewer has already reviewed.
            Do not select the current proposal.
            Do not select a proposal that was written by the reviewer.
            Select a proposal of the same type as the current proposal.
            Select a proposal with the status 'Pending Review'
            Select a random proposal of those remaining.
        """

        # Set up supporting tables
        ConfigFactory(key='password_salt')
        t1 = ProposalTypeFactory()
        t2 = ProposalTypeFactory()
        withdrawn = ProposalStatusFactory(name="Withdrawn")
        pending = ProposalStatusFactory(name="Pending Review")
        review_role = RoleFactory(name="reviewer")
        fred = PersonFactory.create(url_hash="XXX")
        db_session.flush()
        r1 = PersonFactory.create()#roles=[review_role])
        r2 = PersonFactory()#roles=[review_role])

        # Query will be for reviewer r1 and type t1
        # Set up a bunch of proposals, some good, some bad
        # Store their id in a good and bad list for verification
        good = []
        bad = []

        # Unreviewed proposals
        for i in range(10):
            prop = ProposalFactory(type=t1, status=pending)
            good.append(prop.id)

        # Withdrawn proposals
        for i in range(3):
            prop = ProposalFactory(type=t1, status=withdrawn)
            bad.append(prop.id)

        # Other status proposals
        for i in range(3):
            prop = ProposalFactory(type=t1, status=ProposalStatusFactory())
            bad.append(prop.id)

        # Reviewed proposals
        for i in range(5):
            prop = ProposalFactory(type=t1, status=pending)
            ReviewFactory(reviewer=r1, proposal=prop)
            bad.append(prop.id)

        # Proposals reviewed by other reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1, status=pending)
            ReviewFactory(reviewer=r2, proposal=prop)
            good.append(prop.id)

        # Proposals reviewed by both reviewers
        for i in range(3):
            prop = ProposalFactory(type=t1, status=pending)
            ReviewFactory(reviewer=r1, proposal=prop)
            ReviewFactory(reviewer=r2, proposal=prop)
            bad.append(prop.id)

        # Proposals written by reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r1], status=pending)
            bad.append(prop.id)

        # Proposals written by other reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r2], status=pending)
            good.append(prop.id)

        # Proposals written by both reviewers
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r1, r2], status=pending)
            bad.append(prop.id)

        # Proposals of wrong type
        for i in range(5):
            prop = ProposalFactory(type=t2, status=pending)
            bad.append(prop.id)

        frequency = {x:0 for x in good}

        for i in range(1000):
            current = Proposal.find_by_id(random.choice(good))
            fetched = Proposal.find_next_proposal(current, r1)
            assert fetched != current
            assert fetched.id in good
            assert fetched.id not in bad
            frequency[fetched.id] += 1

        # Ensure an even distribution
        mean = sum(frequency.values())/len(frequency)
        sum_squares = sum((x-mean)**2 for x in frequency.values())
        variance = (sum_squares/len(frequency))**0.5
        assert variance < 20 # Should be around 8-10

    def test_duplicate_titles(self, db_session):
        db_session.execute("CREATE EXTENSION fuzzystrmatch;")
        db_session.execute("CREATE EXTENSION pg_trgm;")
        pending = ProposalStatusFactory(name="Pending Review")

        base        = ProposalFactory(title="An identical title discussing some detail", status=pending)
        duplicate   = ProposalFactory(title="An identical title discussing some detail", status=pending)
        similar     = ProposalFactory(title="An identical title discussing some details", status=pending)
        dissimilar  = ProposalFactory(title="A dissimilar title conversing on a beach", status=pending)
        not_pending = ProposalFactory(title="An identical title discussing some detail", status=ProposalStatusFactory())

        dups = base.find_duplicates()
        assert len(dups) == 2
        assert duplicate in dups
        assert similar in dups

        dups = duplicate.find_duplicates()
        assert len(dups) == 2
        assert base in dups
        assert similar in dups

        dups = similar.find_duplicates()
        assert len(dups) == 2
        assert base in dups
        assert duplicate in dups

        dups = dissimilar.find_duplicates()
        assert len(dups) == 0
        assert dups == []

    def test_duplicate_abstracts(self, db_session):
        db_session.execute("CREATE EXTENSION fuzzystrmatch;")
        db_session.execute("CREATE EXTENSION pg_trgm;")
        withdrawn = ProposalStatusFactory(name="Withdrawn")
        pending = ProposalStatusFactory(name="Pending Review")

        base_abstract = """
            Lorem ipsum dolor sit amet, est meis mentitum ea. Amet appareat nec ne. Ad habeo oblique accumsan usu, summo nobis contentiones ea vix. Duo id iisque discere, nullam principes sit eu. At qui saepe principes voluptatibus.

Eos invidunt interesset at, delectus molestiae suscipiantur eu sea. Lorem offendit ne duo. Nec ut tota tritani temporibus, atqui scripta ad pro. Posse copiosae pri at.

Has ut vidit partiendo posidonium, te liber aperiam nominati sed. An duo magna novum. Usu saepe atomorum in. Possit incorrupte ius in. Inani nullam et vix, in quem suas vivendum per. Est ea unum option eloquentiam.
            """
        similar_abstract = base_abstract.replace("incorrupte", "corrupte")
        similar_abstract = similar_abstract.replace("temporibus", "buspermanentio")

        dissimilar_abstract = """
            Dang ipsizzle dolizzle sit amizzle, ass adipiscing i'm in the shizzle. Nullizzle gangsta velizzle, crazy volutpat, suscipizzle quis, shut the shizzle up vizzle, sizzle. Fizzle eget go to hizzle. Get down get down erizzle. Fizzle dope ghetto shiznit turpis tempus mah nizzle. Fo shizzle my nizzle crazy nibh et turpizzle. Dizzle in crazy. Shizzlin dizzle black rhoncizzle daahng dawg. In hac habitasse platea dictumst. Things dapibizzle. Curabitur gangsta crazy, i'm in the shizzle eu, mattizzle sizzle, eleifend bizzle, nunc. Dawg suscipizzle. Integizzle sempizzle velizzle sizzle boofron.
            """

        base       = ProposalFactory(abstract = base_abstract, status=pending)
        duplicate  = ProposalFactory(abstract = base_abstract, status=pending)
        similar    = ProposalFactory(abstract = similar_abstract, status=pending)
        dissimilar = ProposalFactory(abstract = dissimilar_abstract, status=pending)
        pulled     = ProposalFactory(abstract = base_abstract, status=withdrawn)

        empty1     = ProposalFactory(abstract = "", status=pending)
        empty2     = ProposalFactory(abstract = "", status=pending)
        db_session.commit()

        dups = base.find_duplicates()
        assert len(dups) == 2
        assert duplicate in dups
        assert similar in dups
        assert type(dups[0]) is Proposal

        dups = duplicate.find_duplicates()
        assert len(dups) == 2
        assert base in dups
        assert similar in dups

        dups = similar.find_duplicates()
        assert len(dups) == 2
        assert base in dups
        assert duplicate in dups

        dups = dissimilar.find_duplicates()
        assert len(dups) == 0
        assert dups == []

        dups = empty1.find_duplicates()
        assert len(dups) == 0
        assert dups == []
