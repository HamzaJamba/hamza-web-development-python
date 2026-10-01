from django.db import models


class Payment(models.Model):
    COD = "cod"
    CARD = "card"
    METHOD_CHOICES = [(COD, "Cash on delivery"), (CARD, "Card")]

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    STATUS_CHOICES = [(PENDING, "Pending"), (PAID, "Paid"), (FAILED, "Failed"), (REFUNDED, "Refunded")]

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=40, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} {self.method} {self.status}"
