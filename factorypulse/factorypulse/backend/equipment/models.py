import uuid
from django.db import models


class Machine(models.Model):
    MOTOR, COMPRESSOR, CONVEYOR, PUMP, TURBINE, CNC = "motor", "compressor", "conveyor", "pump", "turbine", "cnc"
    TYPE_CHOICES = [(MOTOR, "Motor"), (COMPRESSOR, "Compressor"), (CONVEYOR, "Conveyor Belt"),
                     (PUMP, "Pump"), (TURBINE, "Turbine"), (CNC, "CNC Machine")]

    RUNNING, IDLE, MAINTENANCE, DOWN = "running", "idle", "maintenance", "down"
    STATUS_CHOICES = [(RUNNING, "Running"), (IDLE, "Idle"), (MAINTENANCE, "In Maintenance"), (DOWN, "Down")]

    LOW, MEDIUM, HIGH, CRITICAL = "low", "medium", "high", "critical"
    CRITICALITY_CHOICES = [(LOW, "Low"), (MEDIUM, "Medium"), (HIGH, "High"), (CRITICAL, "Critical")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    machine_code = models.CharField(max_length=30, unique=True)
    machine_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=MOTOR)
    plant_section = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=150, blank=True)
    manufacturer = models.CharField(max_length=150, blank=True)
    install_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=RUNNING)
    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default=MEDIUM)
    normal_vibration_max = models.DecimalField(max_digits=6, decimal_places=2, default=5.0)
    normal_temperature_max = models.DecimalField(max_digits=6, decimal_places=2, default=80.0)
    normal_pressure_max = models.DecimalField(max_digits=6, decimal_places=2, default=10.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.machine_code})"
