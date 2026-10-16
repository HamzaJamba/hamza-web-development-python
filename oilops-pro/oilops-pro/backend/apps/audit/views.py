from rest_framework import viewsets

from apps.core.permissions import IsAdminRole

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["action", "model", "user"]
    search_fields = ["object_repr", "model", "user__email"]
    ordering_fields = ["timestamp"]
