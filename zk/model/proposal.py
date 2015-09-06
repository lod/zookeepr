"""The application's model objects"""
import sqlalchemy as sa

from meta import Base

from pylons.controllers.util import abort

from meta import Session

from person import Person
from person_proposal_map import person_proposal_map
from attachment import Attachment
from review import Review
from stream import Stream

class ProposalStatus(Base):
    """Stores both account login details and personal information.
    """
    __tablename__ = 'proposal_status'

    id = sa.Column(sa.types.Integer, primary_key=True)

    # title of proposal
    name = sa.Column(sa.types.String(40), unique=True, nullable=False)

    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(ProposalStatus, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, id):
        return Session.query(ProposalStatus).filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return Session.query(ProposalStatus).filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return Session.query(ProposalStatus).order_by(ProposalStatus.name).all()

class ProposalType(Base):
    """Stores both account login details and personal information.
    """
    __tablename__ = 'proposal_type'

    id = sa.Column(sa.types.Integer, primary_key=True)

    # title of proposal
    name = sa.Column(sa.types.String(40), unique=True, nullable=False)
    notify_email = sa.Column(sa.types.Text, nullable=True)

    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(ProposalType, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, id):
        return Session.query(ProposalType).filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return Session.query(ProposalType).filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return Session.query(ProposalType).order_by(ProposalType.name).all()

class TravelAssistanceType(Base):
    __tablename__ = 'travel_assistance_type'

    id = sa.Column(sa.types.Integer, primary_key=True)
    name = sa.Column(sa.types.String(60), unique=True, nullable=False)

    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(TravelAssistanceType, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, id):
        return Session.query(TravelAssistanceType).filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return Session.query(TravelAssistanceType).filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return Session.query(TravelAssistanceType).order_by(TravelAssistanceType.name).all()

class TargetAudience(Base):
    __tablename__ = 'target_audience'

    id = sa.Column(sa.types.Integer, primary_key=True)
    name = sa.Column(sa.types.String(40), unique=True, nullable=False)

    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(TargetAudience, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, id):
        return Session.query(TargetAudience).filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return Session.query(TargetAudience).filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return Session.query(TargetAudience).order_by(TargetAudience.name).all()

class AccommodationAssistanceType(Base):
    __tablename__ = 'accommodation_assistance_type'

    id = sa.Column(sa.types.Integer, primary_key=True)

    # title of proposal
    name = sa.Column(sa.types.String(120), unique=True, nullable=False)

    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(AccommodationAssistanceType, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, id):
        return Session.query(AccommodationAssistanceType).filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return Session.query(AccommodationAssistanceType).filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return Session.query(AccommodationAssistanceType).order_by(AccommodationAssistanceType.name).all()

class Proposal(Base):
    """Stores both account login details and personal information.
    """
    __tablename__ = 'proposal'

    id = sa.Column(sa.types.Integer, primary_key=True)

    # title of proposal
    title = sa.Column(sa.types.Text, nullable=False)
    # abstract or description
    abstract = sa.Column(sa.types.Text, nullable=False)
    private_abstract = sa.Column(sa.types.Text, nullable=True)
    technical_requirements = sa.Column(sa.types.Text, nullable=False)

    # type, enumerated in the proposal_type table
    proposal_type_id = sa.Column(sa.types.Integer, sa.ForeignKey('proposal_type.id'), nullable=False)

    # allocated stream of talk
    stream_id = sa.Column(sa.types.Integer, sa.ForeignKey('stream.id'))

    # type, enumerated in the assistance_type table
    travel_assistance_type_id = sa.Column(sa.types.Integer, sa.ForeignKey('travel_assistance_type.id'), nullable=False)
    accommodation_assistance_type_id = sa.Column(sa.types.Integer, sa.ForeignKey('accommodation_assistance_type.id'), nullable=False)
    status_id = sa.Column(sa.types.Integer, sa.ForeignKey('proposal_status.id'), nullable=False)
    target_audience_id = sa.Column(sa.types.Integer, sa.ForeignKey('target_audience.id'), nullable=False)

    video_release = sa.Column(sa.types.Boolean, nullable=False)
    slides_release = sa.Column(sa.types.Boolean, nullable=False)

    # name and url of the project
    project = sa.Column(sa.types.Text, nullable=False)
    url = sa.Column(sa.types.Text, nullable=True)

    # url to a short video
    abstract_video_url = sa.Column(sa.types.Text, nullable=True)

    creation_timestamp = sa.Column(sa.types.DateTime, nullable=False, default=sa.func.current_timestamp())
    last_modification_timestamp = sa.Column(sa.types.DateTime, nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp())

    # relations
    type = sa.orm.relation(ProposalType, backref='proposals')
    stream = sa.orm.relation(Stream)
    accommodation_assistance = sa.orm.relation(AccommodationAssistanceType)
    travel_assistance = sa.orm.relation(TravelAssistanceType)
    status = sa.orm.relation(ProposalStatus, backref='proposals')
    audience = sa.orm.relation(TargetAudience)
    people = sa.orm.relation(Person, secondary=person_proposal_map, backref='proposals')
    attachments = sa.orm.relation(Attachment, cascade='all, delete-orphan')
    reviews = sa.orm.relation(Review, backref='proposal', cascade='all, delete-orphan')


    def __init__(self, **kwargs):
        # remove the args that should never be set via creation
        super(Proposal, self).__init__(**kwargs)

        stream_id = None

    def __repr__(self):
        return '<Proposal id="%r" title="%s">' % (self.id, self.title)

    def _get_accepted(self):
        return self.status.name == 'Accepted'
    accepted = property(_get_accepted)

    def _get_offered(self):
        return 'Offered' in self.status.name
    offered = property(_get_offered)

    def _get_withdrawn(self):
        return self.status.name == 'Withdrawn'
    withdrawn = property(_get_withdrawn)

    def _get_declined(self):
        return self.status.name == 'Declined'
    declined = property(_get_declined)

    def _get_proposer_status(self):
        if self.accepted or self.withdrawn or self.declined or self.offered:
            return self.status.name
        else:
            return "Under Review"
    proposer_status = property(_get_proposer_status)

    def _get_average_score(self):
        return Session.query(sa.func.avg(Review.score)).filter(Review.proposal_id==self.id, Review.score != None).scalar()
    average_score = property(_get_average_score)

    @classmethod
    def find_by_id(cls, id, abort_404 = True):
        result = Session.query(Proposal).filter_by(id=id).first()
        if result is None and abort_404:
            abort(404, "No such proposal object")
        return result

    @classmethod
    def find_by_title(cls, title):
        return Session.query(Proposal).filter_by(title=title).order_by(Proposal.title).all()

    @classmethod
    def find_all(cls):
        return Session.query(Proposal).order_by(Proposal.id).all()

    @classmethod
    def count_all(cls):
        return Session.query(Proposal).count()

    @classmethod
    def find_all_by_accommodation_assistance_type_id(cls, id, abort_404 = True):
        result = Session.query(Proposal).filter_by(accommodation_assistance_type_id=id).all()
        if result is None and abort_404:
            abort(404, "No such proposal object")
        return result

    @classmethod
    def find_all_by_travel_assistance_type_id(cls, id, abort_404 = True):
        result = Session.query(Proposal).filter_by(travel_assistance_type_id=id).all()
        if result is None and abort_404:
            abort(404, "No such proposal object")
        return result

    @classmethod
    def find_all_accepted(cls):
        return Session.query(Proposal).filter(ProposalStatus.name=='Accepted')

    @classmethod
    def find_all_accepted_without_event(cls):
        status = ProposalStatus.find_by_name('Accepted')

        return Session.query(Proposal).filter_by(status=status).filter_by(event=None).all()

    # TODO: Shouldn't be classmethod - current -> self
    @classmethod
    def find_next_proposal(cls, current, person):
        """ Find next proposal for reviewer to review """
        pending = ProposalStatus.find_by_name('Pending Review')
        q = Session.query(Proposal).from_statement(sa.text("""
                SELECT p.id FROM (
                        SELECT id
                        FROM proposal
                        WHERE id <> %d
                        AND status_id = %d
                        AND proposal_type_id = %d
                    EXCEPT
                        SELECT proposal_id AS id
                        FROM review
                        WHERE review.reviewer_id = %d
                    EXCEPT
                        SELECT proposal_id AS id
                        FROM person_proposal_map
                        WHERE person_id = %d
                ) as p
                ORDER BY RANDOM()
                LIMIT 1
        """ % (current.id, pending.id, current.type.id, person.id, person.id)))
        next = q.first()
        if next is not None:
            return cls.find_by_id(next.id, abort_404=False)
        else:
            # looks like you've reviewed everything!
            return None

    def find_duplicates(self):
        pending = ProposalStatus.find_by_name('Pending Review')

        # Use advanced database options if they are available
        if Session.get_bind().name == 'postgresql':
            # Use two different text comparison algorithms
            # levenshtein calculates the number of character changes required
            # to convert one string to another, it is good for small blocks of text.
            # similarity from pg_trgm uses trigrams, it creates groups of three
            # letters and performs a frequency analysis. This is good for larger
            # blocks of text but bad for short sentences.
            # 
            # levenshtein_less_equal requires the fuzzystrmatch extension
            # similarity requires the pg_trgm extension
            # Both are distributed with Postgresql 9.4 but not part of the core

            # Significant performance optimization on similarity
            # % operation is equivilent to: similarity(p1.abstract, p2.abstract) > 0.8
            # Resulting performance is fairly good, cost=8.44..20.49
            # On the 2016 full submission data set my ancient laptop takes
            # 0.3ms to plan, 4.5ms to execute
            # The identical match is not too much faster: 0.15..52.48, 0.3ms, 1.1ms
            Session.execute("SELECT set_limit(0.8)")

            return Session.query(Proposal).from_statement(sa.text("""
                    SELECT p2.id
                    FROM proposal as p1, proposal as p2
                    WHERE p1.id <> p2.id
                    AND p1.id = %d
                    AND p2.status_id = %d
                    AND (
                        p1.title %% p2.title
                        OR
                        p1.abstract %% p2.abstract
                    )
                """ % (self.id, pending.id))).all()
        else:
            # Fallback option - just do an identical text match
            return Session.query(Proposal).from_statement(sa.text("""
                    SELECT p2.id
                    FROM proposal as p1, proposal as p2
                    WHERE p1.id <> p2.id
                    AND p1.id = %d
                    AND p2.status_id = %d
                    AND (
                        p1.title = p2.title
                        OR
                        p1.abstract = p2.abstract
                    )
                """ % (self.id, pending.id))).all()
