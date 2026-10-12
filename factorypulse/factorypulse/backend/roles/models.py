from django.db import models


class Role(models.Model):
    ADMIN = "admin"
    PLANT_MANAGER = "plant_manager"
    MAINTENANCE_ENGINEER = "maintenance_engineer"
    OPERATOR = "operator"
    ROLE_CHOICES = [
        (ADMIN, "Admin"), (PLANT_MANAGER, "Plant Manager"),
        (MAINTENANCE_ENGINEER, "Maintenance Engineer"), (OPERATOR, "Operator"),
    ]
    name = models.CharField(max_length=30, choices=ROLE_CHOICES, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()

    @classmethod
    def get(cls, name):
        obj, _ = cls.objects.get_or_create(name=name)
        return obj
