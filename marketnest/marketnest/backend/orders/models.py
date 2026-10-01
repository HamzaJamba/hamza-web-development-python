import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models


def new_order_number():
    return "MN-" + uuid.uuid4().hex[:8].upper()


class Order(models.Model):
    PLACED = "placed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PLACED, "Placed"), (PROCESSING, "Processing"), (SHIPPED, "Shipped"),
        (DELIVERED, "Delivered"), (CANCELLED, "Cancelled"),
    ]

    number = models.CharField(max_length=20, unique=True, default=new_order_number, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=PLACED)
    payment_method = models.CharField(max_length=10, default="cod")
    payment_status = models.CharField(max_length=10, default="pending")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=80)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    def refresh_status(self):
        """Derive the order status from its per-stall items."""
        statuses = list(self.items.values_list("status", flat=True))
        active = [s for s in statuses if s != OrderItem.CANCELLED]
        if not active:
            new = self.CANCELLED
        elif all(s == OrderItem.DELIVERED for s in active):
            new = self.DELIVERED
        elif any(s in (OrderItem.SHIPPED, OrderItem.DELIVERED) for s in active):
            new = self.SHIPPED
        elif any(s == OrderItem.PACKED for s in active):
            new = self.PROCESSING
        else:
            new = self.PLACED
        self.status = new
        if new == self.DELIVERED and self.payment_method == "cod":
            self.payment_status = "paid"
            from payments.models import Payment
            from django.utils import timezone
            Payment.objects.filter(order=self).update(status=Payment.PAID, paid_at=timezone.now())
        self.save(update_fields=["status", "payment_status", "updated_at"])


class OrderItem(models.Model):
    PENDING = "pending"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Waiting for the stall"), (PACKED, "Packed"), (SHIPPED, "Shipped"),
        (DELIVERED, "Delivered"), (CANCELLED, "Cancelled"),
    ]
    # what a vendor may move an item to, from where
    TRANSITIONS = {
        PENDING: [PACKED, CANCELLED],
        PACKED: [SHIPPED, CANCELLED],
        SHIPPED: [DELIVERED],
        DELIVERED: [],
        CANCELLED: [],
    }

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.SET_NULL, null=True, related_name="order_items")
    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=160)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
