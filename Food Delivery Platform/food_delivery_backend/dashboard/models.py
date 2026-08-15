from decimal import Decimal
from django.db import models


class PlatformSettings(models.Model):
    """Singleton row (always pk=1) — admin-configurable platform-wide values."""

    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("150.00"))
    tax_rate_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("5.00"), help_text="e.g. 5.00 means 5%"
    )
    rider_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("100.00"))
    platform_commission_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("15.00"),
        help_text="Commission the platform takes from each restaurant order",
    )
    support_email = models.EmailField(default="support@fooddelivery.local")
    support_phone = models.CharField(max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton — never actually deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Platform Settings"
