import uuid
from django.db import models
from fleet.models import Vehicle


class GPSLog(models.Model):
    """A single GPS ping from a vehicle (simulated or real device)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="gps_logs")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    direction_degrees = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altitude_m = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    battery_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["vehicle", "-recorded_at"])]

    def __str__(self):
        return f"{self.vehicle.vehicle_number} @ {self.recorded_at}"


class IoTReading(models.Model):
    """Simulated sensor readings for temperature-sensitive cargo etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="iot_readings")
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure_kpa = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fuel_level_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_alert = models.BooleanField(default=False)
    alert_reason = models.CharField(max_length=200, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    TEMP_LIMIT_HIGH = 8.0  # deg C, e.g. cold-chain breach

    class Meta:
        ordering = ["-recorded_at"]

    def save(self, *args, **kwargs):
        if self.temperature_c is not None and self.temperature_c > self.TEMP_LIMIT_HIGH:
            self.is_alert = True
            self.alert_reason = f"Temperature {self.temperature_c}°C exceeded limit {self.TEMP_LIMIT_HIGH}°C"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} sensor @ {self.recorded_at}"
