from rest_framework import serializers
from .models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    manager_email = serializers.CharField(source="manager.email", read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            "id", "name", "city", "address", "latitude", "longitude",
            "capacity", "manager", "manager_email", "is_active",
            "created_at", "updated_at",
        ]
