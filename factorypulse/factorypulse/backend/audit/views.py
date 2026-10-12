from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer
from roles.permissions import IsAdminRole


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
