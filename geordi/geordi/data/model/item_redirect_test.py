from geordi.test_case import GeordiTestCase
from geordi.data.model.item_redirect import ItemRedirect
from geordi.data.model.item import Item
from . import db


class ItemRedirectTestCase(GeordiTestCase):

    def test_delete(self):
        self.assertEqual(ItemRedirect.query.count(), 0)

        item = Item.create()
        redirect = ItemRedirect(old_id=42, new_id=item.id)
        db.session.add(redirect)
        db.session.flush()

        redirects = ItemRedirect.query.all()
        self.assertEqual(len(redirects), 1)
        self.assertEqual(redirects[0], redirect)

        redirect.delete()

        self.assertEqual(ItemRedirect.query.count(), 0)
