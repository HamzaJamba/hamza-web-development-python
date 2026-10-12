from rest_framework import serializers
from .models import Machine


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = [
            "id", "name", "machine_code", "machine_type", "plant_section", "location",
            "manufacturer", "install_date", "status", "criticality",
            "normal_vibration_max", "normal_temperature_max", "normal_pressure_max",
            "created_at", "updated_at",
        ]
