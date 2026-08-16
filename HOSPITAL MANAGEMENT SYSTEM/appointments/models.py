from django.db import models
from django.conf import settings


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="appointments_booked"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        unique_together = ("doctor", "date", "time")

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} {self.time}"
