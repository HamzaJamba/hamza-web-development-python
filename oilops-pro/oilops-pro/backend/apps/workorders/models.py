from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class WorkOrder(TimeStampedModel):
    class Type(models.TextChoices):
        PREVENTIVE = "PREVENTIVE", "Preventive"
        CORRECTIVE = "CORRECTIVE", "Corrective"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        ON_HOLD = "ON_HOLD", "On hold"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    OPEN_STATUSES = ("OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD")

    number = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.PROTECT, related_name="work_orders")
    wo_type = models.CharField(max_length=15, choices=Type.choices, default=Type.CORRECTIVE, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM, db_index=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_work_orders")
    engineer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="engineered_work_orders")
    technicians = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="assigned_work_orders")
    schedule = models.ForeignKey("maintenance.MaintenanceSchedule", null=True, blank=True, on_delete=models.SET_NULL, related_name="work_orders")
    incident = models.ForeignKey("incidents.Incident", null=True, blank=True, on_delete=models.SET_NULL, related_name="work_orders")
    deadline = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    labor_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    labor_rate = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("35.00"))
    downtime_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.number:
            self.number = f"WO-{timezone.now():%Y}-{self.pk:05d}"
            super().save(update_fields=["number"])

    @property
    def parts_cost(self):
        return sum((p.total_cost for p in self.parts.all()), Decimal("0"))

    @property
    def labor_cost(self):
        return self.labor_hours * self.labor_rate

    @property
    def total_cost(self):
        return self.parts_cost + self.labor_cost

    @property
    def is_overdue(self):
        return bool(self.deadline and self.status in self.OPEN_STATUSES and self.deadline < timezone.now())

    def __str__(self):
        return f"{self.number} {self.title}"


class SparePartUsage(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="parts")
    item = models.ForeignKey("inventory.Item", on_delete=models.PROTECT, related_name="usages")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost
