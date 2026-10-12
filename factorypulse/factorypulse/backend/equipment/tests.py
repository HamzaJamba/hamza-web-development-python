from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from roles.models import Role
from .models import Machine

User = get_user_model()


class MachineTests(APITestCase):
    def setUp(self):
        role = Role.get(Role.ADMIN)
        self.user = User.objects.create_user(email="eng@factorypulse.io", password="StrongPass123", role=role)
        self.client.force_authenticate(user=self.user)

    def test_create_machine(self):
        payload = {"name": "Test Pump", "machine_code": "PMP-99", "machine_type": "pump"}
        response = self.client.post("/api/equipment/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_machine_code_rejected(self):
        payload = {"name": "Test Pump", "machine_code": "PMP-99"}
        self.client.post("/api/equipment/", payload, format="json")
        response = self.client.post("/api/equipment/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/equipment/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_default_status_running(self):
        m = Machine.objects.create(name="Idle Motor", machine_code="MOT-99")
        self.assertEqual(m.status, Machine.RUNNING)
