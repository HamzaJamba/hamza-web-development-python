from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from .models import Driver
from .serializers import DriverSerializer


class DriverViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Driver.objects.all().select_related("assigned_vehicle")
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "assigned_vehicle"]
    search_fields = ["full_name", "license_number", "phone"]
    ordering_fields = ["full_name", "performance_score", "created_at"]
