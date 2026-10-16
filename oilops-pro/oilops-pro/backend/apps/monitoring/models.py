from django.conf import settings
from django.db import models


class Metric(models.TextChoices):
    TEMPERATURE = "TEMPERATURE", "Temperature"
    PRESSURE = "PRESSURE", "Pressure"
    VOLTAGE = "VOLTAGE", "Voltage"
    VIBRATION = "VIBRATION", "Vibration"
    OIL_LEVEL = "OIL_LEVEL", "Oil level"


METRIC_UNITS = {"TEMPERATURE": "°C", "PRESSURE": "bar", "VOLTAGE": "V", "VIBRATION": "mm/s", "OIL_LEVEL": "%"}


class Threshold(models.Model):
    """Limits for a metric. Equipment-specific rows override category-wide rows."""

    class Severity(models.TextChoices):
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    equipment = models.ForeignKey("equipment.Equipment", null=True, blank=True, on_delete=models.CASCADE, related_name="thresholds")
    category = models.CharField(max_length=20, blank=True, help_text="Equipment category when no specific equipment is set")
    metric = models.CharField(max_length=15, choices=Metric.choices, db_index=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.WARNING)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "metric", "severity"]

    def breached_by(self, value):
        return (self.min_value is not None and value < self.min_value) or (self.max_value is not None and value > self.max_value)

    def __str__(self):
        target = self.equipment.serial_number if self.equipment_id else (self.category or "ALL")
        return f"{target} {self.metric} {self.severity} [{self.min_value}, {self.max_value}]"


class SensorReading(models.Model):
    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE, related_name="readings")
    metric = models.CharField(max_length=15, choices=Metric.choices)
    value = models.FloatField()
    recorded_at = models.DateTimeField()

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["equipment", "metric", "-recorded_at"])]


class Alert(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"

    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE, related_name="alerts")
    metric = models.CharField(max_length=15, choices=Metric.choices)
    severity = models.CharField(max_length=10, choices=Threshold.Severity.choices, db_index=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN, db_index=True)
    value = models.FloatField()
    threshold = models.ForeignKey(Threshold, null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts")
    message = models.CharField(max_length=255)
    occurrence_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
