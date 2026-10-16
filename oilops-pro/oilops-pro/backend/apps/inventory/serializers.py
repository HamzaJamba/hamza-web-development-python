from decimal import Decimal

from rest_framework import serializers

from .models import Item, StockMovement
from .services import adjust_stock


class ItemSerializer(serializers.ModelSerializer):
    is_low = serializers.BooleanField(read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    stock_value = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"

    def get_stock_value(self, obj) -> str:
        return str(round(obj.quantity * obj.unit_cost, 2))

    def create(self, validated_data):
        qty = validated_data.pop("quantity", 0)
        item = super().create(validated_data)
        if qty and qty > 0:
            adjust_stock(item.pk, "IN", qty, self.context["request"].user, "OPENING", "Opening balance")
            item.refresh_from_db()
        return item

    def update(self, instance, validated_data):
        validated_data.pop("quantity", None)  # stock only changes through movements
        return super().update(instance, validated_data)


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_sku = serializers.CharField(source="item.sku", read_only=True)
    user_name = serializers.CharField(source="performed_by.full_name", read_only=True, default="")

    class Meta:
        model = StockMovement
        fields = "__all__"


class AdjustSerializer(serializers.Serializer):
    movement_type = serializers.ChoiceField(choices=StockMovement.Type.choices)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0'))
    reference = serializers.CharField(max_length=60, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=255, required=False, allow_blank=True)
