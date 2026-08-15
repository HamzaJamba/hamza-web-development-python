import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model. `role` decides which dashboard/permissions apply."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        RESTAURANT_OWNER = "RESTAURANT_OWNER", "Restaurant Owner"
        RIDER = "RIDER", "Rider"
        CUSTOMER = "CUSTOMER", "Customer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(
        default=True,
        help_text="Used for RESTAURANT_OWNER / RIDER accounts pending admin approval.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Address(models.Model):
    """Reusable delivery address, owned by a Customer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, blank=True, help_text="Home / Work / Other")
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label or 'Address'} - {self.user.username}"
