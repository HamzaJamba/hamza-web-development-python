from django.db import models


class Permission(models.Model):
    """Fine-grained permission, independent of Django's built-in perms."""
    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.codename


class Role(models.Model):
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    RIDER = "rider"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (VENDOR, "Vendor"),
        (CUSTOMER, "Customer"),
        (RIDER, "Delivery Rider"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.CharField(max_length=255, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()

    def has_permission(self, codename):
        return self.permissions.filter(codename=codename).exists()

    @classmethod
    def get(cls, name):
        role, _ = cls.objects.get_or_create(name=name)
        return role
