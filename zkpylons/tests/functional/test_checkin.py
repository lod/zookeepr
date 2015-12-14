from routes import url_for

import json

from .crud_helper import CrudHelper
from .fixtures import PersonFactory, CompletePersonFactory, FulfilmentFactory, FulfilmentTypeFactory, FulfilmentStatusFactory, FulfilmentItemFactory, ProductFactory, RegoNoteFactory, RegistrationFactory, FulfilmentGroupFactory
from .utils import do_login

class TestCheckin(object):
    def test_permissions(self, app, db_session):
        # All pages can be accessed by either the organiser or checkin role
        pages = ('lookup', 'person_data', 'update_fulfilments', 'get_talk')

        target = CompletePersonFactory()

        ch = CrudHelper()
        ch.test_permissions(app, db_session, controller='checkin', target=target, get_pages=pages, post_pages=[], good_roles=['organiser'], ignore_roles=['checkin'])
        ch.test_permissions(app, db_session, controller='checkin', target=target, get_pages=pages, post_pages=[], good_roles=['checkin'], ignore_roles=['organiser'])

    def test_lookup(self, app, db_session):
        # Search based on person.fullname, person.lastname, person.email_address, person.email_address (domain), person.id, FulfilmentGroup.code, Fulfilment.code. Then we return the top 5 hits. All searches are designed to function on partial strings.
        p1 = PersonFactory(firstname="Bobby", lastname="Jones", email_address="jonathon@bobjanes.com")
        p2 = PersonFactory(firstname="Jeff", lastname="Bobbit", email_address="dolly@sheep.baa")
        p3 = PersonFactory(firstname="Dick", lastname="Lightsaber", email_address="scary@lightsabers.com")
        fg1 = FulfilmentGroupFactory(code="Bobster", person=p3)
        f1 = FulfilmentFactory(code="JANE", person=p1)

        user = PersonFactory(roles = [CrudHelper._get_insert_role('organiser')])

        # TODO: Should test 5 limit

        db_session.commit()

        do_login(app, user)

        expected = {
                "Bob" : [
                    {p1.id : "Bobby Jones - jonathon@bobjanes.com"},
                    {p3.id : "Bobster - Dick Lightsaber"},
                    {p2.id : "Jeff Bobbit - dolly@sheep.baa"},
                ],
                "bob" : [
                    {p1.id : "Bobby Jones - jonathon@bobjanes.com"},
                    {p3.id : "Bobster - Dick Lightsaber"},
                    {p2.id : "Jeff Bobbit - dolly@sheep.baa"},
                ],
                "Bobb" : [
                    {p1.id : "Bobby Jones - jonathon@bobjanes.com"},
                    {p2.id : "Jeff Bobbit - dolly@sheep.baa"},
                ],
                "J" : [
                    {p1.id : "Bobby Jones - jonathon@bobjanes.com"},
                    {p1.id : "JANE - Bobby Jones"},
                    {p2.id : "Jeff Bobbit - dolly@sheep.baa"},
                ],
                "Ja" : [
                    {p1.id : "JANE - Bobby Jones"},
                ],
                "Jann" : [
                ],
                p3.id : [
                    {p3.id : "%d - Dick Lightsaber" % p3.id},
                ],
        }

        for stimulus in expected:
            print "STIM", stimulus, type(stimulus)
            resp = app.post(url_for(controller='checkin', action='lookup'), {'q':stimulus})
            print resp.body
            # Build up an expected json string, then compare stringwise
            json_expected = [{"id":int(line.keys()[0]), "pretty":line.values()[0]} for line in expected[stimulus]]
            print json.dumps({"r":json_expected})
            assert resp.body == json.dumps({"r":json_expected})


    def test_person_data(self, app, db_session):
        # Should return a json structure of a person with fulfilments etc.

        initial_status = FulfilmentStatusFactory()
        types = [FulfilmentTypeFactory(initial_status=initial_status) for i in range(10)]
        statuses = [FulfilmentStatusFactory(types=types) for i in range(10)]
        products = [ProductFactory() for i in range(10)]


        p1 = CompletePersonFactory()
        for i in range(10):
            f = FulfilmentFactory(type=types[i], status=statuses[9-i], person=p1)
            FulfilmentItemFactory(fulfilment=f, product=products[i], qty=i*2)
            FulfilmentItemFactory(fulfilment=f, product=products[9-i], qty=i*3)

        user = PersonFactory(roles = [CrudHelper._get_insert_role('organiser')])

        rego = RegistrationFactory(person=p1)
        notes = [RegoNoteFactory(rego=rego, by=user) for i in range(5)]

        db_session.commit()


        do_login(app, user)
        resp = app.post(url_for(controller='checkin', action='person_data'), {'id':p1.id})

        assert resp.content_type == 'application/json'

        data = json.loads(resp.body)
        tested = []

        # TODO: Probably shouldn't be exporting the password hash & salt
        person_fields = ('id', 'email_address', 'password_hash', 'password_salt',
                         'url_hash', 'activated', 'firstname', 'lastname',
                         'address1', 'address2', 'city', 'state', 'postcode', 'country', 'company',
                         'phone', 'mobile', 'url', 'experience', 'bio', 'badge_printed', 'i_agree')

        for field in person_fields:
            assert getattr(p1, field) == data.get(field)
            tested.append(field)

        # Problematic datetime fields
        for field in ('last_modification_timestamp', 'creation_timestamp'):
            assert getattr(p1, field).strftime("%d/%m/%Y") == data.get(field)
            tested.append(field)

        assert len(data['fulfilments']) == 10
        for i in range(10):
            f = data['fulfilments'][i]
            assert f['code'] is None
            assert f['id'] == i+1
            assert f['type_id'] == i+1
            assert f['status_id'] == statuses[9-i].id
            assert f['person_id'] == p1.id
            assert f['fulfilment_status'] == statuses[9-i].name
            assert f['fulfilment_type'] == types[i].name
            items = f['fulfilment_items']
            assert len(items) == 2
            for j in range(2):
                # Return is sorted by product_id, so swap order when required
                if i < 5:
                    item = items[j]
                else:
                    item = items[int(not j)]

                product = products[9-i if j else i]
                assert item['fulfilment_id'] == i+1
                assert item['product_id'] == product.id
                assert item['qty'] == (i*2 if not j else i*3)
                assert item['product_text'] is None
                assert item['id'] == i*2 + j
                assert item['description'] == 'product category %03d - factory generated product %03d'%(product.category.id, product.id)
                for k in item.keys():
                    assert k in ['fulfilment_id', 'product_id', 'qty', 'product_text', 'id', 'description']
            for k in f.keys():
                assert k in ['code', 'id', 'type_id', 'status_id', 'person_id', 'fulfilment_status', 'fulfilment_type', 'fulfilment_items', 'last_modification_timestamp', 'creation_timestamp']
        tested.append('fulfilments')

        assert len(data['notes']) == 5
        for i in range(5):
            note = data['notes'][i]
            assert note['by_id'] == user.id
            assert note['note'] == notes[i].note # Random
            assert note['rego_id'] == rego.id
            assert note['id'] == i+1
            assert note['block'] == notes[i].block # Random
            for k in note.keys():
                assert k in ['note', 'id', 'by_id', 'rego_id', 'block', 'last_modification_timestamp', 'creation_timestamp']
        tested.append('notes')

        for field in data.keys():
            assert field in tested

    def test_update_fulfilments(self, app, db_session):
        pass # TODO

    def test_get_talk(self, app, db_session):
        pass # TODO - Not sure this function is actually ever used...
