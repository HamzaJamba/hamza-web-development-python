import uuid
from django.db import models
from django.conf import settings
from fleet.models import Vehicle
from drivers.models import Driver
from routes.models import Route
from warehouses.models import Warehouse


class Shipment(models.Model):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    AT_WAREHOUSE = "at_warehouse"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (DRAFT, "Draft"), (PENDING, "Pending"), (APPROVED, "Approved"),
        (ASSIGNED, "Assigned"), (PICKED_UP, "Picked Up"), (IN_TRANSIT, "In Transit"),
        (AT_WAREHOUSE, "At Warehouse"), (OUT_FOR_DELIVERY, "Out For Delivery"),
        (DELIVERED, "Delivered"), (CANCELLED, "Cancelled"),
    ]

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    PRIORITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High"), (URGENT, "Urgent")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_number = models.CharField(max_length=30, unique=True, editable=False)
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)

    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    pickup_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)

    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    volume_cbm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    temperature_sensitive = models.BooleanField(default=False)
    fragile = models.BooleanField(default=False)
    hazardous_material = models.BooleanField(default=False)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    notes = models.TextField(blank=True)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="shipments")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_shipments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"LTP{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_number


class ShipmentAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="shipment_docs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ShipmentStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=Shipment.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
