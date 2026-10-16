import os

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Incident(TimeStampedModel):
    class Type(models.TextChoices):
        GAS_LEAK = "GAS_LEAK", "Gas leak"
        FIRE = "FIRE", "Fire"
        EXPLOSION = "EXPLOSION", "Explosion"
        EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE", "Equipment failure"
        NEAR_MISS = "NEAR_MISS", "Near miss"
        SAFETY_VIOLATION = "SAFETY_VIOLATION", "Safety violation"

    class Severity(models.TextChoices):
        MINOR = "MINOR", "Minor"
        MODERATE = "MODERATE", "Moderate"
        MAJOR = "MAJOR", "Major"
        CATASTROPHIC = "CATASTROPHIC", "Catastrophic"

    class Status(models.TextChoices):
        REPORTED = "REPORTED", "Reported"
        INVESTIGATING = "INVESTIGATING", "Investigating"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    number = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    title = models.CharField(max_length=200)
    incident_type = models.CharField(max_length=20, choices=Type.choices, db_index=True)
    severity = models.CharField(max_length=15, choices=Severity.choices, default=Severity.MINOR, db_index=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REPORTED, db_index=True)
    plant = models.ForeignKey("plants.Plant", on_delete=models.PROTECT, related_name="incidents")
    equipment = models.ForeignKey("equipment.Equipment", null=True, blank=True, on_delete=models.SET_NULL, related_name="incidents")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="reported_incidents")
    occurred_at = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    injuries = models.PositiveSmallIntegerField(default=0)
    downtime_hours = models.DecimalField(max_digits=7, decimal_places=1, default=0)
    estimated_loss = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-occurred_at"]

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.number:
            self.number = f"INC-{timezone.now():%Y}-{self.pk:05d}"
            super().save(update_fields=["number"])

    def __str__(self):
        return f"{self.number} {self.title}"


def attachment_path(instance, filename):
    return f"incidents/{instance.incident_id}/{timezone.now():%Y%m%d%H%M%S}_{os.path.basename(filename)}"


class IncidentAttachment(models.Model):
    class Kind(models.TextChoices):
        PHOTO = "PHOTO", "Photo"
        DOCUMENT = "DOCUMENT", "Document"

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=attachment_path)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.DOCUMENT)
    description = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
