from rest_framework.test import APITestCase
from config.testutils import make_vendor, make_product, make_user, CHECKOUT


class ReviewTests(APITestCase):
    def setUp(self):
        self.vendor = make_vendor()
        self.product = make_product(self.vendor, "Kurta")
        self.a, self.b = make_user("a@test.pk"), make_user("b@test.pk")

    def review(self, user, rating, comment=""):
        self.client.force_authenticate(user)
        return self.client.post("/api/reviews/", {"product": self.product.id, "rating": rating, "comment": comment})

    def test_reviews_update_product_rating(self):
        self.review(self.a, 5); self.review(self.b, 3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 2)
        self.assertEqual(float(self.product.rating_avg), 4.0)

    def test_posting_again_edits_instead_of_duplicating(self):
        self.review(self.a, 2)
        r = self.review(self.a, 5)
        self.assertEqual(r.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating_count, 1)
        self.assertEqual(float(self.product.rating_avg), 5.0)

    def test_rating_must_be_1_to_5(self):
        self.assertEqual(self.review(self.a, 6).status_code, 400)

    def test_verified_purchase_flag(self):
        self.client.force_authenticate(self.a)
        self.client.post("/api/orders/checkout/", {**CHECKOUT, "items": [{"product": self.product.id, "quantity": 1}]}, format="json")
        self.review(self.a, 5); self.review(self.b, 4)
        rows = {r["user_name"]: r["verified_purchase"] for r in self.client.get(f"/api/reviews/?product={self.product.id}").data}
        self.assertTrue(rows["a"]); self.assertFalse(rows["b"])

    def test_anonymous_cannot_post(self):
        self.client.force_authenticate(None)
        r = self.client.post("/api/reviews/", {"product": self.product.id, "rating": 5})
        self.assertEqual(r.status_code, 401)
