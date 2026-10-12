from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from equipment.models import Machine

User = get_user_model()


class DashboardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="dash@factorypulse.io", password="StrongPass123")
        self.client.force_authenticate(user=self.user)

    def test_overview_returns_oee(self):
        Machine.objects.create(name="M1", machine_code="M1", status=Machine.RUNNING)
        Machine.objects.create(name="M2", machine_code="M2", status=Machine.DOWN)
        response = self.client.get("/api/dashboard/overview/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("oee_percent", response.data)
        self.assertEqual(response.data["total_machines"], 2)

    def test_overview_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/dashboard/overview/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
