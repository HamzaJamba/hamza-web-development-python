from rest_framework import serializers

from .models import Pipeline, Plant, StorageTank


class PlantSerializer(serializers.ModelSerializer):
    equipment_count = serializers.IntegerField(read_only=True, default=0)
    tank_count = serializers.IntegerField(read_only=True, default=0)
    manager_name = serializers.CharField(source="manager.full_name", read_only=True, default="")
    plant_type_display = serializers.CharField(source="get_plant_type_display", read_only=True)

    class Meta:
        model = Plant
        fields = "__all__"


class PipelineSerializer(serializers.ModelSerializer):
    origin_name = serializers.CharField(source="origin.name", read_only=True)
    destination_name = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Pipeline
        fields = "__all__"

    def validate(self, attrs):
        o = attrs.get("origin", getattr(self.instance, "origin", None))
        d = attrs.get("destination", getattr(self.instance, "destination", None))
        if o and d and o == d:
            raise serializers.ValidationError("Origin and destination must differ.")
        return attrs


class StorageTankSerializer(serializers.ModelSerializer):
    fill_percent = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)
    plant_name = serializers.CharField(source="plant.name", read_only=True)

    class Meta:
        model = StorageTank
        fields = "__all__"

    def validate(self, attrs):
        cap = attrs.get("capacity_litres", getattr(self.instance, "capacity_litres", None))
        lvl = attrs.get("current_level_litres", getattr(self.instance, "current_level_litres", 0))
        if cap is not None and lvl > cap:
            raise serializers.ValidationError({"current_level_litres": "Level cannot exceed capacity."})
        return attrs
