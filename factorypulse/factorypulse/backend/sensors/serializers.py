from rest_framework import serializers
from .models import SensorReading


class SensorReadingSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(source="machine.machine_code", read_only=True)

    class Meta:
        model = SensorReading
        fields = ["id", "machine", "machine_code", "vibration_mm_s", "temperature_c", "pressure_bar",
                  "rpm", "is_anomaly", "anomaly_score", "recorded_at"]
        read_only_fields = ["is_anomaly", "anomaly_score"]
