from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")


class IsRestaurantOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role == "RESTAURANT_OWNER"
        )


class IsRider(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "RIDER")


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "CUSTOMER")


class IsOwnerOrAdmin(BasePermission):
    """Object-level: only the object's owner (however that's defined) or an Admin can write."""

    owner_field = "owner"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == "ADMIN":
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner == request.user


class IsRestaurantApproved(BasePermission):
    """Blocks write access for restaurant owners whose account is pending approval."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.role != "RESTAURANT_OWNER":
            return True
        return user.is_approved
