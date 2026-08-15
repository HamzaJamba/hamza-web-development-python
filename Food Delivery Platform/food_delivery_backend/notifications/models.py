import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER_PLACED = "ORDER_PLACED", "Order Placed"
        ORDER_ACCEPTED = "ORDER_ACCEPTED", "Order Accepted"
        FOOD_PREPARING = "FOOD_PREPARING", "Food Preparing"
        RIDER_ASSIGNED = "RIDER_ASSIGNED", "Rider Assigned"
        DELIVERED = "DELIVERED", "Delivered Successfully"
        ORDER_CANCELLED = "ORDER_CANCELLED", "Order Cancelled"
        SYSTEM = "SYSTEM", "System"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=150)
    message = models.CharField(max_length=255)
    related_order_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} -> {self.recipient.username}"
