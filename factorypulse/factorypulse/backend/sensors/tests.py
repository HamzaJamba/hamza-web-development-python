import random
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from equipment.models import Machine
from .models import SensorReading
from .ml import score_reading

User = get_user_model()


class AnomalyScoringTests(APITestCase):
    def setUp(self):
        self.machine = Machine.objects.create(
            name="Test Motor", machine_code="MOT-TEST",
            normal_vibration_max=Decimal("5.0"), normal_temperature_max=Decimal("80.0"), normal_pressure_max=Decimal("10.0"),
        )

    def test_fallback_threshold_flags_extreme_reading_with_no_history(self):
        is_anomaly, score = score_reading(self.machine, vibration=50, temperature=200, pressure=300, rpm=1000)
        self.assertTrue(is_anomaly)
        self.assertIsNone(score)

    def test_fallback_does_not_flag_reading_within_limits(self):
        is_anomaly, score = score_reading(self.machine, vibration=2, temperature=40, pressure=5, rpm=1000)
        self.assertFalse(is_anomaly)

    def test_ml_model_trains_once_enough_history_exists(self):
        random.seed(42)
        for i in range(60):
            SensorReading.objects.create(
                machine=self.machine,
                vibration_mm_s=Decimal(str(round(2.0 + random.uniform(-0.3, 0.3), 2))),
                temperature_c=Decimal(str(round(40.0 + random.uniform(-2, 2), 2))),
                pressure_bar=Decimal(str(round(5.0 + random.uniform(-0.2, 0.2), 2))),
                rpm=1500,
            )
        is_anomaly, score = score_reading(self.machine, vibration=2.0, temperature=40.0, pressure=5.0, rpm=1500)
        self.assertIsNotNone(score)
        self.assertFalse(is_anomaly)
        is_anomaly2, score2 = score_reading(self.machine, vibration=80.0, temperature=300.0, pressure=400.0, rpm=1500)
        self.assertTrue(is_anomaly2)


class SensorReadingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="op@factorypulse.io", password="StrongPass123")
        self.client.force_authenticate(user=self.user)
        self.machine = Machine.objects.create(name="Test Pump", machine_code="PMP-TEST")

    def test_create_reading_sets_anomaly_fields(self):
        payload = {"machine": str(self.machine.id), "vibration_mm_s": "2.0", "temperature_c": "40.0", "pressure_bar": "5.0", "rpm": 1200}
        response = self.client.post("/api/sensors/readings/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("is_anomaly", response.data)

    def test_list_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/sensors/readings/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
