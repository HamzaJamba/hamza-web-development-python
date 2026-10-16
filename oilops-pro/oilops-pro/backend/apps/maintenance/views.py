from datetime import date, timedelta

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from .models import MaintenanceSchedule
from .serializers import MaintenanceScheduleSerializer
from .tasks import generate_due_work_orders

MAINT = [Role.PLANT_MANAGER, Role.ENGINEER]


class MaintenanceScheduleViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.select_related("equipment", "assigned_engineer")
    serializer_class = MaintenanceScheduleSerializer
    write_roles = MAINT
    filterset_fields = ["equipment", "is_active", "auto_create_work_order", "equipment__plant"]
    search_fields = ["title", "equipment__name", "equipment__serial_number"]
    ordering_fields = ["next_due", "interval_days"]

    @action(detail=False, methods=["get"], pagination_class=None)
    def due(self, request):
        days = int(request.query_params.get("days", 14))
        qs = self.get_queryset().filter(is_active=True, next_due__lte=date.today() + timedelta(days=days))
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["post"], url_path="generate-work-orders")
    def generate(self, request):
        return Response({"created": generate_due_work_orders()})
