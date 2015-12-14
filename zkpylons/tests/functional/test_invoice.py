from zk.model.invoice import Invoice
from zk.model.product_category import ProductCategory
from zkpylons.model.product_category import ProductCategory as pyProductCategory
from .fixtures import PersonFactory, InvoiceFactory, URLHashFactory, InvoiceItemFactory, ProductCategoryFactory, ProductFactory, RegistrationFactory, RegistrationProductFactory, CeilingFactory, ConfigFactory
from .utils import do_login

from routes import url_for

# TODO:
# product_list - json
# new (angular)
# _new
# generate_hash
# index
# remind
# pay
# _pay
# get_invoice - json
# pay_invoice - json
# refund
# pay_manual
# pdf
# void
# unvoid
# extend


class TestInvoiceController(object):
    def test_invoice_view(self, app, db_session):

        ConfigFactory(key="event_parent_organisation", value="TEST-INVOICE-PARENT-ORG")
        ConfigFactory(key="event_tax_number", value="TEST-INVOICE-ABN-NUMBER")

        i = InvoiceFactory()
        InvoiceItemFactory(invoice = i, description='line 1', qty = 2, cost = 100);
        InvoiceItemFactory(invoice = i, qty = 1, cost = 250);
        u = URLHashFactory(url = url_for(controller='invoice', action='view', id=i.id))
        db_session.commit()

        resp = app.get(url_for(controller='invoice', action='view', id=i.id, hash=u.url_hash))

        resp.mustcontain("TEST-INVOICE-PARENT-ORG")
        resp.mustcontain("TEST-INVOICE-ABN-NUMBER")
        resp.mustcontain("line 1") # first entry description
        resp.mustcontain("$2.00")  # first entry subtotal (2x $1)
        resp.mustcontain("$4.50")  # Total

        # TODO
        # Test different permission options
        # Test paid, unpaid and void
        # Test special organiser links


    def test_hash_exploits(self, app, db_session):
        ConfigFactory(key="event_parent_organisation", value="TEST-INVOICE-PARENT-ORG")
        ConfigFactory(key="event_tax_number", value="TEST-INVOICE-ABN-NUMBER")

        # TODO: Delete entries we are testing if they already exist

        i = InvoiceFactory(id=2)
        InvoiceItemFactory(invoice = i, description='line 1', qty = 2, cost = 100);
        InvoiceItemFactory(invoice = i, qty = 1, cost = 250);
        u = URLHashFactory(url = url_for(controller='invoice', action='view', id=i.id))

        target = InvoiceFactory(id=23)
        InvoiceItemFactory(invoice = target, description='line 1', qty = 2, cost = 400);
        InvoiceItemFactory(invoice = target, qty = 1, cost = 850);

        db_session.commit()

        resp = app.get(url_for(controller='invoice', action='view', id=i.id, hash=u.url_hash))
        resp.mustcontain("$4.50") # Total

        # Possible attach where /invoice/2 allows access to /invoice/23
        #resp = app.get(url_for(controller='invoice', action='view', id=target.id, hash=u.url_hash), status = 403)
        print app.get(url_for(controller='invoice', action='view', id=target.id, hash=u.url_hash))



    def test_registration_invoice_gen(self, app, db_session):
        """ testing that we can generate an invoice from a registration """

        cat = ProductCategoryFactory(name = 'Accommodation', note='', min_qty='10', max_qty='100')
        bed = ProductFactory(category = cat, cost = '18500')
        p   = PersonFactory()
        reg = RegistrationFactory(person = p)
        RegistrationProductFactory(registration=reg, product=bed, qty=1)

        # Required for templates
        CeilingFactory(name='conference-earlybird')
        CeilingFactory(name='conference-paid')

        db_session.commit()

        # Invoice is actually generated when looking at the status page
        resp = do_login(app, p)
        resp = app.get('/register/status')
        resp = resp.maybe_follow()
        assert "Tentatively registered" in unicode(resp.body, 'utf-8')

        resp = resp.click('Pay invoice')
        resp = resp.follow() # Generates then redirects to invoice
        assert '/invoice/' in resp.request.path
        assert bed.description in unicode(resp.body, 'utf-8')
        assert str(bed.cost/100) in unicode(resp.body, 'utf-8')

        # Need to forget the objects we created
        bed_id = bed.id
        cat_description = cat.name
        bed_description = bed.description
        db_session.expunge_all()

        inv = Invoice.find_by_person(p.id)
        assert len(inv.items) == 1
        assert inv.items[0].product_id == bed_id
        assert inv.items[0].qty == 1
        assert inv.items[0].free_qty == 0
        # description is category - product
        assert bed_description in inv.items[0].description
        assert cat_description in inv.items[0].description
