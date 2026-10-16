from decimal import Decimal

from django.contrib.auth import get_user_model
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.accounts.serializers import UserBriefSerializer

from .models import SparePartUsage, WorkOrder

User = get_user_model()
ENGINEER_ROLES = {"ENGINEER", "PLANT_MANAGER", "ADMIN"}
TECH_ROLES = {"TECHNICIAN", "ENGINEER"}


class SparePartUsageSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_sku = serializers.CharField(source="item.sku", read_only=True)
    total_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = SparePartUsage
        fields = ["id", "item", "item_name", "item_sku", "quantity", "unit_cost", "total_cost", "created_at"]
        read_only_fields = ["unit_cost", "created_at"]


class WorkOrderSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source="equipment.name", read_only=True)
    equipment_serial = serializers.CharField(source="equipment.serial_number", read_only=True)
    plant = serializers.IntegerField(source="equipment.plant_id", read_only=True)
    plant_name = serializers.CharField(source="equipment.plant.name", read_only=True)
    engineer_name = serializers.CharField(source="engineer.full_name", read_only=True, default="")
    technicians = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(is_active=True), required=False)
    technician_names = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    parts_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    labor_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ["number", "status", "created_by", "started_at", "completed_at", "completion_notes",
                            "labor_hours", "downtime_hours"]

    def get_technician_names(self, obj) -> list[str]:
        return [u.full_name for u in obj.technicians.all()]

    def validate_engineer(self, user):
        if user and user.role not in ENGINEER_ROLES:
            raise serializers.ValidationError("Engineer must have an engineering or management role.")
        return user

    def validate_technicians(self, users):
        bad = [u.email for u in users if u.role not in TECH_ROLES]
        if bad:
            raise serializers.ValidationError(f"Not technicians: {', '.join(bad)}")
        return users

    def validate_deadline(self, value):
        if self.instance is None and value and value < timezone.now() - timedelta(minutes=5):
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def create(self, validated_data):
        techs = validated_data.pop("technicians", [])
        wo = WorkOrder.objects.create(created_by=self.context["request"].user, **validated_data)
        from . import services
        if techs or wo.engineer_id:
            services.assign(wo, wo.engineer, techs, self.context["request"].user)
        return wo

    def update(self, instance, validated_data):
        techs = validated_data.pop("technicians", None)
        super().update(instance, validated_data)
        if techs is not None:
            instance.technicians.set(techs)
        return instance


class WorkOrderDetailSerializer(WorkOrderSerializer):
    parts = SparePartUsageSerializer(many=True, read_only=True)
    engineer_detail = UserBriefSerializer(source="engineer", read_only=True)


class AssignSerializer(serializers.Serializer):
    engineer = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), required=False)
    technicians = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(is_active=True), required=False)


class CompleteSerializer(serializers.Serializer):
    completion_notes = serializers.CharField()
    labor_hours = serializers.DecimalField(max_digits=6, decimal_places=1, required=False, min_value=Decimal('0'))
    downtime_hours = serializers.DecimalField(max_digits=6, decimal_places=1, required=False, min_value=Decimal('0'))


class ReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class AddPartSerializer(serializers.Serializer):
    item = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
