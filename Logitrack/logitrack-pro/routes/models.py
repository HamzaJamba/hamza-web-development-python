import uuid
from django.db import models


class Route(models.Model):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PLANNED, "Planned"), (ACTIVE, "Active"),
        (COMPLETED, "Completed"), (CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_time_minutes = models.PositiveIntegerField()
    toll_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
