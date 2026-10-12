from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_superuser or (u.role and u.role.name == "admin")))


class IsPlantManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (
            u.is_superuser or (u.role and u.role.name in ("admin", "plant_manager"))
        ))


class IsMaintenanceStaff(BasePermission):
    """Engineers, managers, and admins can act on maintenance; operators are read-mostly."""
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (
            u.is_superuser or (u.role and u.role.name in ("admin", "plant_manager", "maintenance_engineer"))
        ))
