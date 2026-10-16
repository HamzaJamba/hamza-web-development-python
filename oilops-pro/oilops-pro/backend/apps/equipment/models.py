from datetime import date

from django.db import models

from apps.core.models import TimeStampedModel


class Equipment(TimeStampedModel):
    class Category(models.TextChoices):
        PUMP = "PUMP", "Pump"
        COMPRESSOR = "COMPRESSOR", "Compressor"
        VALVE = "VALVE", "Valve"
        GENERATOR = "GENERATOR", "Generator"
        TURBINE = "TURBINE", "Turbine"
        SENSOR = "SENSOR", "Sensor"

    class Status(models.TextChoices):
        OPERATIONAL = "OPERATIONAL", "Operational"
        MAINTENANCE = "MAINTENANCE", "Under maintenance"
        FAULTY = "FAULTY", "Faulty"
        OFFLINE = "OFFLINE", "Offline"
        DECOMMISSIONED = "DECOMMISSIONED", "Decommissioned"

    class Criticality(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    plant = models.ForeignKey("plants.Plant", on_delete=models.PROTECT, related_name="equipment")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    serial_number = models.CharField(max_length=80, unique=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL, db_index=True)
    criticality = models.CharField(max_length=10, choices=Criticality.choices, default=Criticality.MEDIUM)
    location_note = models.CharField(max_length=150, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    health_score = models.PositiveSmallIntegerField(default=100, help_text="0-100, maintained by monitoring")

    class Meta(TimeStampedModel.Meta):
        ordering = ["plant", "name"]

    @property
    def warranty_active(self):
        return bool(self.warranty_expiry and self.warranty_expiry >= date.today())

    @property
    def maintenance_overdue(self):
        return bool(self.next_maintenance_date and self.next_maintenance_date < date.today()
                    and self.status != self.Status.DECOMMISSIONED)

    def __str__(self):
        return f"{self.serial_number} {self.name}"
