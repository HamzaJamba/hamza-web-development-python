from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from roles.permissions import IsPlantManagerOrAdmin
from .models import Machine
from .serializers import MachineSerializer


class MachineViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Machine.objects.all().prefetch_related("readings")
    serializer_class = MachineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "machine_type", "criticality", "plant_section"]
    search_fields = ["name", "machine_code", "location"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsPlantManagerOrAdmin()]
        return [permissions.IsAuthenticated()]
