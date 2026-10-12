import uuid
from django.db import models
from equipment.models import Machine


class SensorReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="readings")
    vibration_mm_s = models.DecimalField(max_digits=7, decimal_places=3)
    temperature_c = models.DecimalField(max_digits=6, decimal_places=2)
    pressure_bar = models.DecimalField(max_digits=6, decimal_places=2)
    rpm = models.PositiveIntegerField(default=0)
    is_anomaly = models.BooleanField(default=False)
    anomaly_score = models.FloatField(null=True, blank=True, help_text="Lower = more anomalous (Isolation Forest convention)")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["machine", "-recorded_at"])]

    def __str__(self):
        return f"{self.machine.machine_code} @ {self.recorded_at}"
