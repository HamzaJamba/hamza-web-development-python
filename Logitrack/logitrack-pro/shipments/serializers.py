from rest_framework import serializers
from .models import Shipment, ShipmentAttachment, ShipmentStatusHistory


class ShipmentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentAttachment
        fields = ["id", "shipment", "file", "uploaded_at"]


class ShipmentStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source="changed_by.email", read_only=True)

    class Meta:
        model = ShipmentStatusHistory
        fields = ["id", "status", "changed_by", "changed_by_email", "note", "changed_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True)
    attachments = ShipmentAttachmentSerializer(many=True, read_only=True)
    status_history = ShipmentStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id", "tracking_number", "customer_name", "customer_phone", "customer_email",
            "origin", "destination", "pickup_date", "delivery_date",
            "weight_kg", "volume_cbm", "temperature_sensitive", "fragile", "hazardous_material",
            "priority", "status", "notes",
            "vehicle", "vehicle_number", "driver", "driver_name", "route", "warehouse",
            "created_by", "attachments", "status_history", "created_at", "updated_at",
        ]
        read_only_fields = ["tracking_number", "created_by"]


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)
