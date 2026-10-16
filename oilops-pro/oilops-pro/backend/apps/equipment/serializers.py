from rest_framework import serializers

from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source="plant.name", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    warranty_active = serializers.BooleanField(read_only=True)
    maintenance_overdue = serializers.BooleanField(read_only=True)
    open_alerts = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Equipment
        fields = "__all__"
        read_only_fields = ["health_score"]

    def validate(self, attrs):
        g = lambda k: attrs.get(k, getattr(self.instance, k, None))  # noqa: E731
        if g("purchase_date") and g("warranty_expiry") and g("warranty_expiry") < g("purchase_date"):
            raise serializers.ValidationError({"warranty_expiry": "Warranty cannot expire before purchase."})
        if g("last_service_date") and g("next_maintenance_date") and g("next_maintenance_date") < g("last_service_date"):
            raise serializers.ValidationError({"next_maintenance_date": "Next maintenance cannot precede last service."})
        return attrs
