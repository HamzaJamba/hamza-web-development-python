import uuid
from django.db import models


class Vehicle(models.Model):
    TRUCK = "truck"
    VAN = "van"
    TRAILER = "trailer"
    CONTAINER = "container"
    TYPE_CHOICES = [(TRUCK, "Truck"), (VAN, "Van"), (TRAILER, "Trailer"), (CONTAINER, "Container")]

    DIESEL = "diesel"
    PETROL = "petrol"
    ELECTRIC = "electric"
    CNG = "cng"
    FUEL_CHOICES = [(DIESEL, "Diesel"), (PETROL, "Petrol"), (ELECTRIC, "Electric"), (CNG, "CNG")]

    AVAILABLE = "available"
    ON_TRIP = "on_trip"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    STATUS_CHOICES = [
        (AVAILABLE, "Available"), (ON_TRIP, "On Trip"),
        (MAINTENANCE, "In Maintenance"), (OUT_OF_SERVICE, "Out of Service"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_number = models.CharField(max_length=30, unique=True)
    truck_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TRUCK)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default=DIESEL)
    fuel_consumption_per_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    insurance_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    last_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["vehicle_number"]

    def __str__(self):
        return self.vehicle_number


class MaintenanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="maintenance_records")
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.service_date}"
