from datetime import date

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Department(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return self.name


class Position(TimeStampedModel):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="positions")

    class Meta(TimeStampedModel.Meta):
        ordering = ["department", "title"]
        unique_together = [("title", "department")]

    def __str__(self):
        return f"{self.title} ({self.department.code})"


class Shift(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta(TimeStampedModel.Meta):
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M}-{self.end_time:%H:%M})"


class SalaryGrade(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=60)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta(TimeStampedModel.Meta):
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Employee(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On leave"
        TERMINATED = "TERMINATED", "Terminated"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="employee")
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name="employees")
    shift = models.ForeignKey(Shift, null=True, blank=True, on_delete=models.SET_NULL, related_name="employees")
    salary_grade = models.ForeignKey(SalaryGrade, null=True, blank=True, on_delete=models.SET_NULL, related_name="employees")
    plant = models.ForeignKey("plants.Plant", null=True, blank=True, on_delete=models.SET_NULL, related_name="employees")
    hire_date = models.DateField(default=date.today)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    photo = models.ImageField(upload_to="employees/", null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.employee_id} {self.full_name}"


class TrainingRecord(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="trainings")
    title = models.CharField(max_length=150)
    provider = models.CharField(max_length=120, blank=True)
    completed_on = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-completed_on"]


class Certification(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=120, blank=True)
    certificate_no = models.CharField(max_length=60, blank=True)
    issued_on = models.DateField()
    expires_on = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to="certifications/", null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["expires_on"]

    @property
    def is_expired(self):
        return bool(self.expires_on and self.expires_on < date.today())
