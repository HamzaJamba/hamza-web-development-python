from datetime import date, timedelta

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class MaintenanceSchedule(TimeStampedModel):
    """Recurring preventive maintenance plan for one piece of equipment."""

    equipment = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE, related_name="schedules")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    interval_days = models.PositiveIntegerField(default=90)
    last_performed = models.DateField(null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    assigned_engineer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    auto_create_work_order = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["next_due"]

    def save(self, *args, **kwargs):
        if not self.next_due:
            self.next_due = (self.last_performed or date.today()) + timedelta(days=self.interval_days)
        super().save(*args, **kwargs)
        self.sync_equipment()

    def sync_equipment(self):
        nxt = (MaintenanceSchedule.objects.filter(equipment=self.equipment, is_active=True)
               .exclude(next_due__isnull=True).order_by("next_due").values_list("next_due", flat=True).first())
        if nxt != self.equipment.next_maintenance_date:
            self.equipment.next_maintenance_date = nxt
            self.equipment.save(update_fields=["next_maintenance_date", "updated_at"])

    def mark_performed(self, on=None):
        on = on or date.today()
        self.last_performed = on
        self.next_due = on + timedelta(days=self.interval_days)
        self.save()

    @property
    def is_overdue(self):
        return bool(self.next_due and self.next_due < date.today() and self.is_active)

    def __str__(self):
        return f"{self.equipment.serial_number}: {self.title}"
