import uuid
from django.conf import settings
from django.db import models
from orders.models import Order


class Rider(models.Model):
    class CnicStatus(models.TextChoices):
        NOT_SUBMITTED = "NOT_SUBMITTED", "Not Submitted"
        PENDING = "PENDING", "Pending Review"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rider_profile"
    )
    vehicle_type = models.CharField(max_length=50, blank=True)
    vehicle_number = models.CharField(max_length=30, blank=True)
    cnic_number = models.CharField(max_length=20, blank=True)
    cnic_status = models.CharField(max_length=20, choices=CnicStatus.choices, default=CnicStatus.NOT_SUBMITTED)
    cnic_rejection_reason = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deliveries = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Rider - {self.user.username}"


class Delivery(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery")
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, related_name="deliveries")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_fee_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Delivery for {self.order.order_number}"
