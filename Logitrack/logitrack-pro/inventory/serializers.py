from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id", "product_name", "category", "warehouse", "warehouse_name",
            "quantity", "unit", "minimum_stock", "maximum_stock", "is_low_stock",
            "created_at", "updated_at",
        ]
