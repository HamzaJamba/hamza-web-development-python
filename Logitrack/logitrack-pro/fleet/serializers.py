from rest_framework import serializers
from .models import Vehicle, MaintenanceRecord


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = ["id", "vehicle", "description", "cost", "service_date", "next_due_date", "created_at"]


class VehicleSerializer(serializers.ModelSerializer):
    maintenance_records = MaintenanceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id", "vehicle_number", "truck_type", "capacity_kg", "fuel_type",
            "fuel_consumption_per_km", "insurance_number", "insurance_expiry",
            "registration_number", "status", "last_maintenance_date",
            "maintenance_records", "created_at", "updated_at",
        ]
