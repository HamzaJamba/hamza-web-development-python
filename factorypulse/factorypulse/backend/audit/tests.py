from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from roles.models import Role
from .models import AuditLog

User = get_user_model()


class AuditLogTests(APITestCase):
    def setUp(self):
        role = Role.get(Role.MAINTENANCE_ENGINEER)
        self.user = User.objects.create_user(email="audit@factorypulse.io", password="StrongPass123", role=role)
        self.client.force_authenticate(user=self.user)

    def test_creating_work_order_writes_audit_log(self):
        from equipment.models import Machine
        machine = Machine.objects.create(name="Audit Test Machine", machine_code="AUD-01")
        self.client.post("/api/maintenance/work-orders/", {"machine": str(machine.id), "title": "Check valve"}, format="json")
        self.assertTrue(AuditLog.objects.filter(model_name="WorkOrder", action=AuditLog.CREATE).exists())

    def test_only_admin_can_view_audit_logs(self):
        response = self.client.get("/api/audit/logs/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
