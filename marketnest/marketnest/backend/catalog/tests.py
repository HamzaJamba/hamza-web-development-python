from rest_framework.test import APITestCase
from config.testutils import make_vendor, make_product, make_category, make_user
from roles.models import Role


class CatalogTests(APITestCase):
    def setUp(self):
        self.vendor = make_vendor()
        self.fashion = make_category("fashion", "Fashion")
        self.tech = make_category("electronics", "Electronics")
        make_product(self.vendor, "Lawn Kurta", "3000", category=self.fashion)
        make_product(self.vendor, "Wireless Earbuds", "7000", category=self.tech)

    def test_public_can_list_products(self):
        r = self.client.get("/api/catalog/products/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)

    def test_filter_by_category_and_price(self):
        r = self.client.get("/api/catalog/products/?category=electronics")
        self.assertEqual([p["name"] for p in r.data["results"]], ["Wireless Earbuds"])
        r = self.client.get("/api/catalog/products/?max_price=4000")
        self.assertEqual([p["name"] for p in r.data["results"]], ["Lawn Kurta"])

    def test_search(self):
        r = self.client.get("/api/catalog/products/?search=earbuds")
        self.assertEqual(r.data["count"], 1)

    def test_unapproved_vendor_products_hidden(self):
        hidden = make_vendor("new@test.pk", "Pending Stall", approved=False)
        make_product(hidden, "Secret Item")
        r = self.client.get("/api/catalog/products/")
        self.assertNotIn("Secret Item", [p["name"] for p in r.data["results"]])

    def test_vendor_can_create_product_but_customer_cannot(self):
        payload = {"name": "New Shawl", "price": "2500", "stock": 5, "category_id": self.fashion.id}
        self.client.force_authenticate(make_user("cust@test.pk"))
        self.assertEqual(self.client.post("/api/catalog/products/", payload).status_code, 403)
        self.client.force_authenticate(self.vendor.owner)
        r = self.client.post("/api/catalog/products/", payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["vendor"]["slug"], self.vendor.slug)

    def test_vendor_cannot_edit_another_vendors_product(self):
        other = make_vendor("other@test.pk", "Other Stall")
        theirs = make_product(other, "Their Thing")
        self.client.force_authenticate(self.vendor.owner)
        r = self.client.patch(f"/api/catalog/products/{theirs.slug}/", {"price": "1"})
        self.assertEqual(r.status_code, 404)

    def test_compare_price_must_exceed_price(self):
        self.client.force_authenticate(self.vendor.owner)
        r = self.client.post("/api/catalog/products/", {
            "name": "Bad", "price": "2000", "compare_at_price": "1500", "stock": 1, "category_id": self.fashion.id})
        self.assertEqual(r.status_code, 400)
