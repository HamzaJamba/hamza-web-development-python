from django.db import models
from django.conf import settings


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    class BloodGroup(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, choices=BloodGroup.choices, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="patients/", blank=True, null=True)
    registered_date = models.DateField(auto_now_add=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="patients_registered"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-registered_date"]

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last = Patient.objects.order_by("id").last()
            next_id = (last.id + 1) if last else 1
            self.patient_id = f"PAT-{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.patient_id})"


class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_history")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.SET_NULL, null=True, related_name="diagnoses")
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to="medical_history/", blank=True, null=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Medical histories"

    def __str__(self):
        return f"{self.patient} - {self.diagnosis} ({self.date})"
