from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from equipment.models import Machine
from sensors.models import SensorReading
from roles.models import Role
from .models import WorkOrder
from .predict import predict_remaining_life

User = get_user_model()


class PredictiveMaintenanceTests(APITestCase):
    def setUp(self):
        self.machine = Machine.objects.create(name="Degrading Pump", machine_code="PMP-DEG", normal_vibration_max=Decimal("5.0"))

    def test_not_enough_data_returns_none(self):
        self.assertIsNone(predict_remaining_life(self.machine))

    def test_stable_trend_detected(self):
        base = timezone.now() - timedelta(hours=20)
        for i in range(15):
            r = SensorReading.objects.create(machine=self.machine, vibration_mm_s=Decimal("2.0"), temperature_c=Decimal("40.0"), pressure_bar=Decimal("5.0"), rpm=1000)
            SensorReading.objects.filter(pk=r.pk).update(recorded_at=base + timedelta(hours=i))
        result = predict_remaining_life(self.machine)
        self.assertEqual(result["trend"], "stable_or_improving")

    def test_degrading_trend_predicts_remaining_hours(self):
        base = timezone.now() - timedelta(hours=14)
        for i in range(15):
            vib = Decimal(str(1.0 + i * 0.1))  # rising from 1.0 to 2.4, well under the 5.0 limit
            r = SensorReading.objects.create(machine=self.machine, vibration_mm_s=vib, temperature_c=Decimal("40.0"), pressure_bar=Decimal("5.0"), rpm=1000)
            SensorReading.objects.filter(pk=r.pk).update(recorded_at=base + timedelta(hours=i))
        result = predict_remaining_life(self.machine)
        self.assertEqual(result["trend"], "degrading")
        self.assertIsNotNone(result["remaining_hours"])


class WorkOrderAPITests(APITestCase):
    def setUp(self):
        role = Role.get(Role.MAINTENANCE_ENGINEER)
        self.user = User.objects.create_user(email="mgr@factorypulse.io", password="StrongPass123", role=role)
        self.client.force_authenticate(user=self.user)
        self.machine = Machine.objects.create(name="Test Mill", machine_code="CNC-TEST")

    def test_create_work_order(self):
        payload = {"machine": str(self.machine.id), "title": "Replace bearing", "priority": "high"}
        response = self.client.post("/api/maintenance/work-orders/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_work_order_defaults_to_open(self):
        wo = WorkOrder.objects.create(machine=self.machine, title="Inspect belt")
        self.assertEqual(wo.status, WorkOrder.OPEN)
