from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from audit.mixins import AuditLogMixin
from audit.models import AuditLog
from roles.models import Role
from roles.permissions import IsAdminRole
from .models import Vendor
from .serializers import VendorSerializer


def annotated(qs):
    return qs.annotate(
        product_count=Count("products", filter=Q(products__is_active=True), distinct=True),
        rating_calc=Avg("products__rating_avg", filter=Q(products__rating_count__gt=0)),
    )


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    """Public stalls list/detail plus apply / me / approve actions."""
    serializer_class = VendorSerializer
    lookup_field = "slug"
    pagination_class = None
    filterset_fields = ["city"]
    search_fields = ["shop_name", "tagline"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "approve":
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return annotated(Vendor.objects.filter(is_approved=True))

    @action(detail=False, methods=["post"])
    def apply(self, request):
        if hasattr(request.user, "vendor"):
            return Response({"detail": "You already have a stall application."}, status=status.HTTP_400_BAD_REQUEST)
        ser = VendorSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        vendor = ser.save(owner=request.user)
        return Response(VendorSerializer(vendor).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        vendor = getattr(request.user, "vendor", None)
        if vendor is None:
            return Response({"detail": "You have not applied for a stall yet."}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "PATCH":
            ser = VendorSerializer(vendor, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
        return Response(VendorSerializer(vendor).data)

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        if not (request.user.is_superuser or (request.user.role and request.user.role.name == Role.ADMIN)):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(VendorSerializer(Vendor.objects.filter(is_approved=False), many=True).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, slug=None):
        vendor = get_object_or_404(Vendor, slug=slug)
        vendor.is_approved = True
        vendor.save()
        vendor.owner.role = Role.get(Role.VENDOR)
        vendor.owner.save()
        AuditLog.objects.create(user=request.user, action=AuditLog.UPDATE, model_name="Vendor",
                                object_id=str(vendor.pk), object_repr=f"approved {vendor}", path=request.path)
        return Response(VendorSerializer(vendor).data)
