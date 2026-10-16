from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        MAINTENANCE_DUE = "MAINTENANCE_DUE", "Maintenance due"
        LOW_STOCK = "LOW_STOCK", "Low stock"
        INCIDENT = "INCIDENT", "Incident"
        ALERT = "ALERT", "Sensor alert"
        WORK_ORDER = "WORK_ORDER", "Work order"
        CERTIFICATION = "CERTIFICATION", "Certification"
        SYSTEM = "SYSTEM", "System"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SYSTEM, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=10, default="info")  # info | warning | critical
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read"])]

    def __str__(self):
        return f"{self.user_id}: {self.title}"
