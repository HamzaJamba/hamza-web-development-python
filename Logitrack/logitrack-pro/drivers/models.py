import uuid
from django.db import models
from django.conf import settings
from fleet.models import Vehicle


class Driver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_profile", null=True, blank=True
    )
    full_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=100, unique=True)
    license_expiry = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    assigned_vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_drivers"
    )
    performance_score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
