from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")

    def test_register_and_login(self):
        payload = {"email": "newengineer@factorypulse.io", "first_name": "New", "last_name": "Engineer",
                   "password": "StrongPass123", "password2": "StrongPass123"}
        r1 = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = self.client.post(self.login_url, {"email": payload["email"], "password": "StrongPass123"}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn("access", r2.data)

    def test_login_wrong_password_fails(self):
        User.objects.create_user(email="x@factorypulse.io", password="StrongPass123")
        response = self.client.post(self.login_url, {"email": "x@factorypulse.io", "password": "wrong"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_auth(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
