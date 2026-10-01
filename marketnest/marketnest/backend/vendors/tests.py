from rest_framework.test import APITestCase
from config.testutils import make_user, make_vendor
from roles.models import Role


class VendorTests(APITestCase):
    def test_register_gives_customer_role_and_login_returns_it(self):
        payload = {"email": "new@test.pk", "first_name": "N", "last_name": "U", "phone": "03001112222",
                   "password": "StrongPass123", "password2": "StrongPass123"}
        self.assertEqual(self.client.post("/api/auth/register/", payload).status_code, 201)
        r = self.client.post("/api/auth/login/", {"email": "new@test.pk", "password": "StrongPass123"})
        self.assertEqual(r.data["user"]["role"], "customer")

    def test_apply_then_admin_approves(self):
        user = make_user("owner@test.pk")
        self.client.force_authenticate(user)
        r = self.client.post("/api/vendors/apply/", {"shop_name": "Fresh Stall", "city": "Lahore"})
        self.assertEqual(r.status_code, 201)
        slug = r.data["slug"]
        self.assertFalse(r.data["is_approved"])
        self.assertEqual(self.client.get("/api/vendors/").data, [])          # not public yet

        self.assertEqual(self.client.post(f"/api/vendors/{slug}/approve/").status_code, 403)
        self.client.force_authenticate(make_user("boss@test.pk", Role.ADMIN))
        self.assertEqual(self.client.post(f"/api/vendors/{slug}/approve/").status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.role.name, "vendor")
        self.assertEqual(len(self.client.get("/api/vendors/").data), 1)

    def test_cannot_apply_twice(self):
        user = make_user("owner@test.pk")
        self.client.force_authenticate(user)
        self.client.post("/api/vendors/apply/", {"shop_name": "One"})
        self.assertEqual(self.client.post("/api/vendors/apply/", {"shop_name": "Two"}).status_code, 400)

    def test_bad_awning_colour_rejected(self):
        self.client.force_authenticate(make_user("owner@test.pk"))
        r = self.client.post("/api/vendors/apply/", {"shop_name": "X", "awning_primary": "blue"})
        self.assertEqual(r.status_code, 400)
