from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Plant(TimeStampedModel):
    class Type(models.TextChoices):
        PLANT = "PLANT", "Processing plant"
        REFINERY = "REFINERY", "Refinery"
        GAS_STATION = "GAS_STATION", "Gas station"
        TERMINAL = "TERMINAL", "Storage terminal"

    class Status(models.TextChoices):
        OPERATIONAL = "OPERATIONAL", "Operational"
        MAINTENANCE = "MAINTENANCE", "Under maintenance"
        SHUTDOWN = "SHUTDOWN", "Shut down"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    plant_type = models.CharField(max_length=20, choices=Type.choices, default=Type.PLANT, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity_bpd = models.PositiveIntegerField(default=0, help_text="Barrels per day")
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_plants")
    commissioned_on = models.DateField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Pipeline(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        IDLE = "IDLE", "Idle"
        MAINTENANCE = "MAINTENANCE", "Under maintenance"
        DECOMMISSIONED = "DECOMMISSIONED", "Decommissioned"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    origin = models.ForeignKey(Plant, on_delete=models.PROTECT, related_name="outgoing_pipelines")
    destination = models.ForeignKey(Plant, on_delete=models.PROTECT, related_name="incoming_pipelines")
    product = models.CharField(max_length=60, default="Crude oil")
    length_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    diameter_inch = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    max_pressure_bar = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta(TimeStampedModel.Meta):
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.origin.code} -> {self.destination.code})"


class StorageTank(TimeStampedModel):
    class Product(models.TextChoices):
        CRUDE = "CRUDE", "Crude oil"
        DIESEL = "DIESEL", "Diesel"
        PETROL = "PETROL", "Petrol"
        KEROSENE = "KEROSENE", "Kerosene"
        LPG = "LPG", "LPG"
        NATURAL_GAS = "NATURAL_GAS", "Natural gas"

    class Status(models.TextChoices):
        IN_SERVICE = "IN_SERVICE", "In service"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of service"
        INSPECTION = "INSPECTION", "Under inspection"

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="tanks")
    tag = models.CharField(max_length=30)
    product = models.CharField(max_length=20, choices=Product.choices, default=Product.CRUDE)
    capacity_litres = models.DecimalField(max_digits=14, decimal_places=2)
    current_level_litres = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_SERVICE)
    last_inspection = models.DateField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["plant", "tag"]
        unique_together = [("plant", "tag")]

    @property
    def fill_percent(self):
        if not self.capacity_litres:
            return Decimal("0")
        return round(self.current_level_litres / self.capacity_litres * 100, 1)

    def __str__(self):
        return f"{self.plant.code}/{self.tag}"
