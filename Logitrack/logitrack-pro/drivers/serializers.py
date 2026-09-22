from rest_framework import serializers
from .models import Driver


class DriverSerializer(serializers.ModelSerializer):
    assigned_vehicle_number = serializers.CharField(source="assigned_vehicle.vehicle_number", read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id", "user", "full_name", "license_number", "license_expiry", "phone",
            "email", "emergency_contact", "address", "assigned_vehicle",
            "assigned_vehicle_number", "performance_score", "is_active",
            "created_at", "updated_at",
        ]
