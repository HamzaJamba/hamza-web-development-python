from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from .models import Equipment
from .serializers import EquipmentSerializer


class EquipmentViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = EquipmentSerializer
    write_roles = [Role.PLANT_MANAGER, Role.ENGINEER]
    filterset_fields = ["plant", "category", "status", "criticality"]
    search_fields = ["name", "serial_number", "manufacturer", "model_number"]
    ordering_fields = ["name", "health_score", "next_maintenance_date", "purchase_date"]

    def get_queryset(self):
        return Equipment.objects.select_related("plant").annotate(
            open_alerts=Count("alerts", filter=Q(alerts__status__in=["OPEN", "ACKNOWLEDGED"]), distinct=True))

    @action(detail=True, methods=["get"], url_path="work-orders")
    def work_orders(self, request, pk=None):
        from apps.workorders.serializers import WorkOrderSerializer

        qs = self.get_object().work_orders.select_related("equipment", "engineer").order_by("-created_at")[:50]
        return Response(WorkOrderSerializer(qs, many=True).data)
