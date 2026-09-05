from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsHotelOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'hotel_owner')


class IsTourOperator(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'tour_operator')


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'customer')


class IsOwnerOrAdmin(BasePermission):
    """Object-level permission: only the owner of the object or an admin can edit it."""
    def has_object_permission(self, request, view, obj):
        owner_field = getattr(obj, 'owner', None) or getattr(obj, 'operator', None) or getattr(obj, 'user', None)
        return request.user.role == 'admin' or owner_field == request.user
