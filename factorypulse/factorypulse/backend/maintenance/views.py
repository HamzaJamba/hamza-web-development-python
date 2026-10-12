from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from audit.models import AuditLog
from roles.permissions import IsMaintenanceStaff
from equipment.models import Machine
from .models import WorkOrder
from .serializers import WorkOrderSerializer
from .predict import predict_remaining_life


class WorkOrderViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().select_related("machine", "assigned_to")
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "machine", "assigned_to"]
    search_fields = ["title", "machine__name", "machine__machine_code"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "complete"):
            return [permissions.IsAuthenticated(), IsMaintenanceStaff()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self._log(AuditLog.CREATE, instance)
        return instance

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = WorkOrder.COMPLETED
        order.completed_at = timezone.now()
        order.resolution_notes = request.data.get("resolution_notes", order.resolution_notes)
        order.save()
        self._log(AuditLog.UPDATE, order)
        return Response(WorkOrderSerializer(order).data)


class PredictiveMaintenanceView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        try:
            machine = Machine.objects.get(pk=pk)
        except Machine.DoesNotExist:
            return Response({"detail": "Machine not found."}, status=status.HTTP_404_NOT_FOUND)
        prediction = predict_remaining_life(machine)
        if prediction is None:
            return Response({"trend": "insufficient_data", "message": "Not enough sensor history yet to predict a trend."})
        return Response(prediction)
