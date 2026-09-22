from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogSerializer
from roles.permissions import IsAdminRole


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only, read-only view of the audit trail."""
    queryset = AuditLog.objects.all().select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["action", "model_name", "user"]
    ordering_fields = ["timestamp"]
