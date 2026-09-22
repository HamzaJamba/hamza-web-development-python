from decimal import Decimal
from django.test import TestCase
from fleet.models import Vehicle
from .models import IoTReading


class IoTAlertTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(vehicle_number="TRK-001", capacity_kg=5000)

    def test_high_temperature_triggers_alert(self):
        reading = IoTReading.objects.create(vehicle=self.vehicle, temperature_c=Decimal("12.5"))
        self.assertTrue(reading.is_alert)
        self.assertIn("exceeded limit", reading.alert_reason)

    def test_normal_temperature_no_alert(self):
        reading = IoTReading.objects.create(vehicle=self.vehicle, temperature_c=Decimal("4.0"))
        self.assertFalse(reading.is_alert)
