from rest_framework import serializers

from .models import MaintenanceSchedule


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_serial = serializers.CharField(source="equipment.serial_number", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = "__all__"

    def validate_interval_days(self, v):
        if v < 1:
            raise serializers.ValidationError("Interval must be at least 1 day.")
        return v
