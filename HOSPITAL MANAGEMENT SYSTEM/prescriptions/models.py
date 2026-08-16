from django.db import models


class Prescription(models.Model):
    appointment = models.ForeignKey(
        "appointments.Appointment", on_delete=models.SET_NULL, null=True, blank=True, related_name="prescriptions"
    )
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.CASCADE, related_name="prescriptions")
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor} ({self.date})"


class Medicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="medicines")
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, help_text="e.g. 1-0-1")
    duration = models.CharField(max_length=50, help_text="e.g. 5 days")
    instructions = models.CharField(max_length=150, blank=True, help_text="e.g. after meal")

    def __str__(self):
        return f"{self.name} ({self.dosage})"
