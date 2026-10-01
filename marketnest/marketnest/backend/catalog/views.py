from django.db.models import Count, Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from audit.mixins import AuditLogMixin
from vendors.permissions import IsApprovedVendor
from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count("products", filter=Q(products__is_active=True, products__vendor__is_approved=True))
        )


class ProductViewSet(AuditLogMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "vendor__shop_name", "category__name"]
    ordering_fields = ["price", "created_at", "rating_avg", "sold_count"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsApprovedVendor()]

    def get_queryset(self):
        base = Product.objects.select_related("vendor", "category")
        if self.action in ("update", "partial_update", "destroy", "mine"):
            return base.filter(vendor__owner=self.request.user)
        return base.filter(is_active=True, vendor__is_approved=True)

    def perform_create(self, serializer):
        instance = serializer.save(vendor=self.request.user.vendor)
        self._log("create", instance)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)
