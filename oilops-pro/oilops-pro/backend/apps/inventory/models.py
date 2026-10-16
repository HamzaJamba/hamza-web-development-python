from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Item(TimeStampedModel):
    class Category(models.TextChoices):
        SPARE_PART = "SPARE_PART", "Spare part"
        CHEMICAL = "CHEMICAL", "Chemical"
        LUBRICANT = "LUBRICANT", "Lubricant"
        SAFETY = "SAFETY", "Safety equipment"

    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    unit = models.CharField(max_length=20, default="pcs")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True)
    plant = models.ForeignKey("plants.Plant", null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_items")
    supplier = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]

    @property
    def is_low(self):
        return self.quantity <= self.reorder_level

    def __str__(self):
        return f"{self.sku} {self.name}"


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = "IN", "Stock in"
        OUT = "OUT", "Stock out"
        ADJUST = "ADJUST", "Adjustment (set level)"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=10, choices=Type.choices, db_index=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=60, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
