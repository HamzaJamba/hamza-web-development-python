import uuid
from django.db import models
from django.conf import settings
from equipment.models import Machine


class WorkOrder(models.Model):
    LOW, MEDIUM, HIGH, CRITICAL = "low", "medium", "high", "critical"
    PRIORITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High"), (CRITICAL, "Critical")]

    OPEN, IN_PROGRESS, COMPLETED, CANCELLED = "open", "in_progress", "completed", "cancelled"
    STATUS_CHOICES = [(OPEN, "Open"), (IN_PROGRESS, "In Progress"), (COMPLETED, "Completed"), (CANCELLED, "Cancelled")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="work_orders")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_work_orders")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_work_orders")
    is_ai_generated = models.BooleanField(default=False, help_text="True if auto-created from a predictive maintenance alert")
    due_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.machine.machine_code})"
