from rest_framework import serializers
from .models import WorkOrder


class WorkOrderSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source="machine.name", read_only=True)
    machine_code = serializers.CharField(source="machine.machine_code", read_only=True)
    assigned_to_email = serializers.CharField(source="assigned_to.email", read_only=True)

    class Meta:
        model = WorkOrder
        fields = ["id", "machine", "machine_name", "machine_code", "title", "description", "priority", "status",
                  "assigned_to", "assigned_to_email", "created_by", "is_ai_generated", "due_date",
                  "resolution_notes", "created_at", "completed_at"]
        read_only_fields = ["created_by", "is_ai_generated"]
