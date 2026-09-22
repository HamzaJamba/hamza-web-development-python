from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from .models import Vehicle, MaintenanceRecord
from .serializers import VehicleSerializer, MaintenanceRecordSerializer


class VehicleViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().prefetch_related("maintenance_records")
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "truck_type", "fuel_type"]
    search_fields = ["vehicle_number", "registration_number"]
    ordering_fields = ["vehicle_number", "created_at"]


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["vehicle"]
