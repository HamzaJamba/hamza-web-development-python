import uuid
from django.conf import settings
from django.db import models
from menu.models import FoodItem
from restaurants.models import Restaurant
from accounts.models import Address


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "PERCENT", "Percentage"
        FLAT = "FLAT", "Flat Amount"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1, help_text="Total redemptions allowed")
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        PREPARING = "PREPARING", "Preparing"
        READY_FOR_PICKUP = "READY_FOR_PICKUP", "Ready for Pickup"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="+")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    platform_commission_percent_snapshot = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Commission rate at the time this order was placed (rate can change later without affecting old orders)",
    )
    platform_commission_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Platform's cut, calculated on subtotal (food revenue), not delivery/tax",
    )
    restaurant_payout = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="What the restaurant actually receives: subtotal minus platform commission",
    )

    placed_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["restaurant", "status"]),
            models.Index(fields=["customer", "status"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, related_name="+")
    food_name_snapshot = models.CharField(max_length=150, help_text="Name at time of order, in case item is later edited/deleted")
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    special_instructions = models.CharField(max_length=255, blank=True)

    @property
    def line_total(self):
        return self.unit_price_snapshot * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.food_name_snapshot}"
