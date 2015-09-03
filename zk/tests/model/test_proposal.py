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
            Do not select a proposal that has been withdrawn.
            Do not select the current proposal.
            Do not select a proposal that was written by the reviewer.
            Select a proposal of the same type as the current proposal.
            Select a random proposal of those remaining.
        """

        # Set up supporting tables
        ConfigFactory(key='password_salt')
        t1 = ProposalTypeFactory()
        t2 = ProposalTypeFactory()
        withdrawn = ProposalStatusFactory(name="Withdrawn")
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
            prop = ProposalFactory(type=t1)
            good.append(prop.id)

        # Withdrawn proposals
        for i in range(3):
            prop = ProposalFactory(type=t1, status=withdrawn)
            bad.append(prop.id)

        # Reviewed proposals
        for i in range(5):
            prop = ProposalFactory(type=t1)
            ReviewFactory(reviewer=r1, proposal=prop)
            bad.append(prop.id)

        # Proposals reviewed by other reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1)
            ReviewFactory(reviewer=r2, proposal=prop)
            good.append(prop.id)

        # Proposals reviewed by both reviewers
        for i in range(3):
            prop = ProposalFactory(type=t1)
            ReviewFactory(reviewer=r1, proposal=prop)
            ReviewFactory(reviewer=r2, proposal=prop)
            bad.append(prop.id)

        # Proposals written by reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r1])
            bad.append(prop.id)

        # Proposals written by other reviewer
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r2])
            good.append(prop.id)

        # Proposals written by both reviewers
        for i in range(5):
            prop = ProposalFactory(type=t1, people=[r1, r2])
            bad.append(prop.id)

        # Proposals of wrong type
        for i in range(5):
            prop = ProposalFactory(type=t2)
            bad.append(prop.id)

        frequency = {x:0 for x in good}
        db_session.commit()

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

