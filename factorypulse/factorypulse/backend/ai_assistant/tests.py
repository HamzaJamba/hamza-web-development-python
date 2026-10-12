from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from equipment.models import Machine
from .services import explain_machine

User = get_user_model()


class AIAssistantTests(APITestCase):
    def setUp(self):
        self.machine = Machine.objects.create(name="Test Compressor", machine_code="CMP-TEST")

    def test_fallback_explanation_when_no_api_key(self):
        result = explain_machine(self.machine)
        self.assertEqual(result["source"], "fallback")
        self.assertIn("Test Compressor", result["answer"])

    def test_fallback_mentions_no_anomalies_when_clean(self):
        result = explain_machine(self.machine)
        self.assertIn("No anomalies", result["answer"])


class AskAssistantAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="eng2@factorypulse.io", password="StrongPass123")
        self.client.force_authenticate(user=self.user)
        self.machine = Machine.objects.create(name="Test Turbine", machine_code="TRB-TEST")

    def test_ask_requires_valid_machine_id(self):
        response = self.client.post("/api/ai/ask/", {"machine_id": "not-a-real-id"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ask_returns_explanation(self):
        response = self.client.post("/api/ai/ask/", {"machine_id": str(self.machine.id)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("answer", response.data)

    def test_ask_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/ai/ask/", {"machine_id": str(self.machine.id)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
