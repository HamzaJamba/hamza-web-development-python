from rest_framework import serializers
from .models import GPSLog, IoTReading


class GPSLogSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)

    class Meta:
        model = GPSLog
        fields = [
            "id", "vehicle", "vehicle_number", "latitude", "longitude", "speed_kmh",
            "direction_degrees", "altitude_m", "current_city", "battery_percent", "recorded_at",
        ]


class IoTReadingSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)

    class Meta:
        model = IoTReading
        fields = [
            "id", "vehicle", "vehicle_number", "temperature_c", "humidity_percent",
            "pressure_kpa", "fuel_level_percent", "is_alert", "alert_reason", "recorded_at",
        ]
        read_only_fields = ["is_alert", "alert_reason"]
