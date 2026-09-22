from django.db import models


class Permission(models.Model):
    """Custom fine-grained permission, independent of Django's default perms."""
    codename = models.CharField(max_length=100, unique=True)  # e.g. "shipment.create"
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.codename


class Role(models.Model):
    ADMIN = "admin"
    OPERATIONS_MANAGER = "operations_manager"
    WAREHOUSE_MANAGER = "warehouse_manager"
    FLEET_MANAGER = "fleet_manager"
    DRIVER = "driver"
    DISPATCHER = "dispatcher"
    VIEWER = "viewer"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (OPERATIONS_MANAGER, "Operations Manager"),
        (WAREHOUSE_MANAGER, "Warehouse Manager"),
        (FLEET_MANAGER, "Fleet Manager"),
        (DRIVER, "Driver"),
        (DISPATCHER, "Dispatcher"),
        (VIEWER, "Viewer (Read Only)"),
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
