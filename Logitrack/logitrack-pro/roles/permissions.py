"""
Reusable DRF permission classes based on the Role & Permission system.
Usage in a view: permission_classes = [IsAuthenticated, HasRolePermission]
and set: required_permission = "shipment.create" as a class attribute on the view.
"""
from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        required = getattr(view, "required_permission", None)
        if required is None:
            return True  # no restriction declared
        role = getattr(request.user, "role", None)
        if not role:
            return False
        return role.has_permission(required)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (user.is_superuser or (user.role and user.role.name == "admin"))
        )
