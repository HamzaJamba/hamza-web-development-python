from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"

    role = models.CharField(max_length=15, choices=Role.choices, default=Role.RECEPTIONIST)
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
