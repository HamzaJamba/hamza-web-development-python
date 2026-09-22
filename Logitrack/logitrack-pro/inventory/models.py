import uuid
from django.db import models
from warehouses.models import Warehouse


class InventoryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory_items")
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=30, default="pcs")
    minimum_stock = models.PositiveIntegerField(default=0)
    maximum_stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_name"]

    def __str__(self):
        return f"{self.product_name} @ {self.warehouse.name}"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock
