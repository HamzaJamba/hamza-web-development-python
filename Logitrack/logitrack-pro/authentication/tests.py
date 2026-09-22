from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.valid_payload = {
            "email": "driver1@logitrack.com",
            "first_name": "Ali",
            "last_name": "Khan",
            "phone": "03001234567",
            "password": "StrongPass123",
            "password2": "StrongPass123",
        }

    def test_register_creates_user(self):
        response = self.client.post(self.register_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="driver1@logitrack.com").exists())

    def test_register_password_mismatch_fails(self):
        payload = self.valid_payload.copy()
        payload["password2"] = "Mismatch123"
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_jwt(self):
        User.objects.create_user(email="driver1@logitrack.com", password="StrongPass123")
        response = self.client.post(
            self.login_url, {"email": "driver1@logitrack.com", "password": "StrongPass123"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_fails(self):
        User.objects.create_user(email="driver1@logitrack.com", password="StrongPass123")
        response = self.client.post(
            self.login_url, {"email": "driver1@logitrack.com", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
