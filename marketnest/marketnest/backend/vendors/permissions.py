from rest_framework.permissions import BasePermission


class IsApprovedVendor(BasePermission):
    message = "Only approved vendors can do this."

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and hasattr(u, "vendor") and u.vendor.is_approved)
