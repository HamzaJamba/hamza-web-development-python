from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdmin, IsRestaurantOwner, IsOwnerOrAdmin
from .models import Restaurant, WorkingHour
from .serializers import (
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    RestaurantCreateSerializer,
    RestaurantApprovalSerializer,
    WorkingHourSerializer,
)


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    GET /api/restaurants/                -> public, only APPROVED restaurants shown
    GET /api/restaurants/{id}/           -> public detail
    POST /api/restaurants/               -> RESTAURANT_OWNER only, creates as PENDING
    PATCH/PUT /api/restaurants/{id}/     -> owner (their own) or admin
    DELETE /api/restaurants/{id}/        -> owner or admin
    POST /api/restaurants/{id}/approve/  -> admin only
    POST /api/restaurants/{id}/toggle-open/ -> owner only
    """

    queryset = Restaurant.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["city", "status"]
    search_fields = ["name", "city"]
    ordering_fields = ["avg_rating", "created_at", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return RestaurantListSerializer
        if self.action == "create":
            return RestaurantCreateSerializer
        if self.action == "approve":
            return RestaurantApprovalSerializer
        return RestaurantDetailSerializer

    def get_permissions(self):
        if self.action in ("create",):
            return [permissions.IsAuthenticated(), IsRestaurantOwner()]
        if self.action in ("update", "partial_update", "destroy", "toggle_open"):
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        if self.action == "approve":
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Restaurant.objects.all()
        if self.action == "list":
            # Public listing only shows approved + open-for-business restaurants
            qs = qs.filter(status=Restaurant.Status.APPROVED)
        return qs

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        restaurant = self.get_object()
        new_status = request.data.get("status", Restaurant.Status.APPROVED)
        restaurant.status = new_status
        restaurant.save(update_fields=["status"])
        return Response(RestaurantDetailSerializer(restaurant).data)

    @action(detail=True, methods=["post"], url_path="toggle-open")
    def toggle_open(self, request, pk=None):
        restaurant = self.get_object()
        restaurant.is_open = not restaurant.is_open
        restaurant.save(update_fields=["is_open"])
        return Response({"is_open": restaurant.is_open})

    @action(detail=False, methods=["get"], url_path="mine", permission_classes=[permissions.IsAuthenticated, IsRestaurantOwner])
    def mine(self, request):
        qs = Restaurant.objects.filter(owner=request.user)
        return Response(RestaurantDetailSerializer(qs, many=True).data)


class WorkingHourViewSet(viewsets.ModelViewSet):
    """Nested under a restaurant the owner controls: /api/restaurants/{restaurant_pk}/hours/"""

    serializer_class = WorkingHourSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return WorkingHour.objects.filter(
            restaurant_id=self.kwargs["restaurant_pk"], restaurant__owner=self.request.user
        )

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.get(id=self.kwargs["restaurant_pk"], owner=self.request.user)
        serializer.save(restaurant=restaurant)
