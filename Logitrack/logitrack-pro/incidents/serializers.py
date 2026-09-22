from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            "id", "incident_type", "vehicle", "shipment", "description", "location",
            "photo", "status", "reported_by", "reported_at", "resolved_at",
        ]
        read_only_fields = ["reported_by"]
