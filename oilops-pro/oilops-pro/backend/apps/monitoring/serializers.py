from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import METRIC_UNITS, Alert, SensorReading, Threshold


class SensorReadingSerializer(serializers.ModelSerializer):
    recorded_at = serializers.DateTimeField(required=False)
    unit = serializers.SerializerMethodField()

    class Meta:
        model = SensorReading
        fields = ["id", "equipment", "metric", "value", "recorded_at", "unit"]

    def get_unit(self, obj) -> str:
        return METRIC_UNITS.get(obj.metric, "")

    def validate_recorded_at(self, v):
        if v > timezone.now() + timedelta(minutes=5):
            raise serializers.ValidationError("Reading timestamp is in the future.")
        return v

    def validate_equipment(self, eq):
        if eq.status == "DECOMMISSIONED":
            raise serializers.ValidationError("Equipment is decommissioned.")
        return eq


class ThresholdSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True, default="")

    class Meta:
        model = Threshold
        fields = "__all__"

    def validate(self, attrs):
        g = lambda k: attrs.get(k, getattr(self.instance, k, None))  # noqa: E731
        if g("min_value") is None and g("max_value") is None:
            raise serializers.ValidationError("Set at least one of min_value / max_value.")
        if g("min_value") is not None and g("max_value") is not None and g("min_value") > g("max_value"):
            raise serializers.ValidationError("min_value cannot exceed max_value.")
        return attrs


class AlertSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_serial = serializers.CharField(source="equipment.serial_number", read_only=True)
    plant_name = serializers.CharField(source="equipment.plant.name", read_only=True)
    unit = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = "__all__"

    def get_unit(self, obj) -> str:
        return METRIC_UNITS.get(obj.metric, "")
