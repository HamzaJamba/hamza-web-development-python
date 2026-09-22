from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from audit.models import AuditLog
from .models import Shipment, ShipmentStatusHistory
from .serializers import ShipmentSerializer, ShipmentStatusUpdateSerializer


class ShipmentViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Shipment.objects.all().select_related("vehicle", "driver", "route", "warehouse")
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "driver", "vehicle"]
    search_fields = ["tracking_number", "customer_name", "origin", "destination"]
    ordering_fields = ["created_at", "pickup_date", "delivery_date"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self._log(AuditLog.CREATE, instance)
        return instance

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        serializer = ShipmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        note = serializer.validated_data.get("note", "")

        shipment.status = new_status
        shipment.save()
        ShipmentStatusHistory.objects.create(
            shipment=shipment, status=new_status, changed_by=request.user, note=note
        )
        self._log(AuditLog.UPDATE, shipment)
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)
