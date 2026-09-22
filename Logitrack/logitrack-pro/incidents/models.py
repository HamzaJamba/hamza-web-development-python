import uuid
from django.db import models
from django.conf import settings
from fleet.models import Vehicle
from shipments.models import Shipment


class Incident(models.Model):
    ACCIDENT = "accident"
    DELAY = "delay"
    ROAD_CLOSED = "road_closed"
    BREAKDOWN = "vehicle_breakdown"
    FUEL_LEAKAGE = "fuel_leakage"
    TYRE_BURST = "tyre_burst"
    TYPE_CHOICES = [
        (ACCIDENT, "Accident"), (DELAY, "Delay"), (ROAD_CLOSED, "Road Closed"),
        (BREAKDOWN, "Vehicle Breakdown"), (FUEL_LEAKAGE, "Fuel Leakage"), (TYRE_BURST, "Tyre Burst"),
    ]

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    STATUS_CHOICES = [(OPEN, "Open"), (IN_PROGRESS, "In Progress"), (RESOLVED, "Resolved")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to="incidents/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-reported_at"]

    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.reported_at.date()}"
