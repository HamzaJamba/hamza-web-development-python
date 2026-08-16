from django.db import models
from django.conf import settings


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    available_days = models.CharField(max_length=100, blank=True, help_text="e.g. Mon, Wed, Fri")
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["employee_id"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"
