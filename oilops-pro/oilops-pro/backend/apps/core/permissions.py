from rest_framework.permissions import SAFE_METHODS, BasePermission


class RoleBasedPermission(BasePermission):
    """
    RBAC driven by two optional view attributes:

    * ``read_roles``  - roles allowed on safe methods (None = any authenticated user)
    * ``write_roles`` - roles allowed on unsafe methods (None = admins only)
    * ``action_roles`` - {"action_name": roles} overrides for ViewSet actions

    Admins (role=ADMIN or superuser) always pass.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.role == "ADMIN":
            return True
        action = getattr(view, "action", None)
        overrides = getattr(view, "action_roles", {}) or {}
        if action in overrides:
            return user.role in overrides[action]
        if request.method in SAFE_METHODS:
            roles = getattr(view, "read_roles", None)
            return True if roles is None else user.role in roles
        roles = getattr(view, "write_roles", None)
        return False if roles is None else user.role in roles


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_superuser or u.role == "ADMIN"))
