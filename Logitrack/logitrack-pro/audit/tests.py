from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import AuditLog
from roles.models import Role

User = get_user_model()


class AuditLogTests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.user = User.objects.create_user(
            email="ops@logitrack.com", password="StrongPass123", role=self.admin_role
        )
        self.client.force_authenticate(user=self.user)

    def test_creating_shipment_writes_audit_log(self):
        payload = {"customer_name": "Acme", "origin": "Lahore", "destination": "Karachi", "weight_kg": "100"}
        self.client.post("/api/shipments/", payload, format="json")
        self.assertTrue(AuditLog.objects.filter(model_name="Shipment", action=AuditLog.CREATE).exists())

    def test_only_admin_can_view_audit_logs(self):
        viewer_role = Role.objects.create(name=Role.VIEWER)
        viewer = User.objects.create_user(email="viewer2@logitrack.com", password="StrongPass123", role=viewer_role)
        self.client.force_authenticate(user=viewer)
        response = self.client.get("/api/audit/logs/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
