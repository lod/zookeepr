import random

from routes import url_for

from zk.model.attachment import Attachment
from zk.model.proposal import Proposal, ProposalType
from zk.model.person import Person
from zk.model.review import Review
from zk.model.config import Config
from zk.model import TravelAssistanceType, AccommodationAssistanceType

import webtest
from webtest.forms import Upload

from .crud_helper import CrudHelper
from .fixtures import PersonFactory, ProposalFactory, AttachmentFactory, RoleFactory, StreamFactory, ProposalStatusFactory, ProposalTypeFactory, TravelAssistanceTypeFactory, AccommodationAssistanceTypeFactory, TargetAudienceFactory, ConfigFactory, CompletePersonFactory
from .utils import do_login, isSignedIn

class TestMiniconfProposal(CrudHelper):
    def test_permissions(self, app, db_session):
        unactivated = CompletePersonFactory(activated=False)
        activated   = CompletePersonFactory(activated=True)
        ProposalTypeFactory(name='Miniconf')
        db_session.commit()

        CrudHelper.test_permissions(self, app, db_session, page_id=0,
                good_pers=activated, bad_pers=unactivated,
                get_pages=('new', 'index'), post_pages=('new',)
        )


    def test_new(self, app, db_session, smtplib):
        ConfigFactory(category='general', key='cfmini_status', value='closed')
        activated   = CompletePersonFactory(activated=True)
        db_session.commit()

        # Call-for-papers must be open to submit a paper
        expected = [ "The call for miniconfs is now closed" ]
        url = url_for(controller='miniconf_proposal', action='new', id=None)
        CrudHelper.test_view(self, app, db_session, url=url, user=activated, title="Closed", expected=expected)

        # Try not-open
        Config.find_by_pk(('general','cfmini_status')).value = 'not_open'
        db_session.commit()

        expected = [ "The call for miniconfs is not yet open" ]
        CrudHelper.test_view(self, app, db_session, url=url, user=activated, title="Coming soon", expected=expected)


        if TravelAssistanceType.find_by_id(1) is None:
            TravelAssistanceTypeFactory(id=1)
        if AccommodationAssistanceType.find_by_id(1) is None:
            AccommodationAssistanceTypeFactory(id=1)

        ProposalTypeFactory(name='Miniconf')
        ProposalStatusFactory(name='Pending Review')
        audiences = [ TargetAudienceFactory() for i in range(10) ]
        Config.find_by_pk(('general','cfmini_status')).value = 'open'
        db_session.commit()

        expected = {
                'title'            : 'Group hug miniconf',
                'abstract'         : 'We all stand around in a group and hug, then we pair off and hug, there will be hug demonstrations and discussions followed by workshops of different hug techniques.',
                'private_abstract' : 'I am cognisant of the risk that some participants may be overly enthusiastic in hugging the opposite gender. The organiser will carry a cattle prod to manage this risk, a bucket of water will be placed outside the door to cool off persistent cases. The risk of applying both a cattle prod and water are unclear but the organiser looks forward to finding out.',
                'audience'         : random.choice(audiences).id,
                'url'              : 'http://group.hugs/',
        }

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

        def extra_data_check(new):
            pass

        CrudHelper.test_new(self, app, db_session, user=activated, title="Submit a Miniconf", form_prefix='proposal', extra_form_check=extra_form_check, extra_form_set=extra_form_set, extra_data_check=extra_data_check, data=expected, target_class=Proposal, next_url=url_for(controller='proposal', action="index", id=None))


    def test_edit(self):
        pass # No edit function

    def test_view(self):
        pass # No view function

    def test_index(self, app, db_session):
        activated   = CompletePersonFactory(activated=True)
        db_session.commit()

        do_login(app, activated)
        resp = app.get(url_for(controller='miniconf_proposal', action='index', id=None))
        print resp
        assert resp.status_code == 302
        assert url_for(controller='proposal', action='index', id=None) in resp.location


    def test_delete(self):
        pass # No delete function

