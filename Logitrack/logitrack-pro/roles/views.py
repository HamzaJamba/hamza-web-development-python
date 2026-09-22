from rest_framework import viewsets, permissions
from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer
from .permissions import IsAdminRole
from audit.mixins import AuditLogMixin


class RoleViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all().prefetch_related("permissions")
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
