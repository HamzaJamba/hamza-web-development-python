from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from .models import Warehouse
from .serializers import WarehouseSerializer


class WarehouseViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["city", "is_active"]
    search_fields = ["name", "city"]
    ordering_fields = ["name", "capacity", "created_at"]
