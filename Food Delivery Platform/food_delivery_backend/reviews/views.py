from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdmin, IsCustomer
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET  /api/reviews/                 -> public, filter by restaurant or food_item
    POST /api/reviews/                 -> customer only, must own a COMPLETED order
    PATCH /api/reviews/{id}/flag/      -> admin moderation (is_flagged), via generic update
    """

    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["restaurant", "food_item", "is_flagged"]
    ordering_fields = ["created_at", "rating"]

    def get_queryset(self):
        qs = Review.objects.select_related("customer").prefetch_related("images")
        if self.action == "list":
            qs = qs.filter(is_flagged=False)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCustomer()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "review_create"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def flag(self, request, pk=None):
        """POST /api/reviews/{id}/flag/ — admin hides a review from public listing (moderation)."""
        review = self.get_object()
        review.is_flagged = True
        review.save(update_fields=["is_flagged"])
        return Response(ReviewSerializer(review, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def unflag(self, request, pk=None):
        """POST /api/reviews/{id}/unflag/ — admin restores a previously flagged review."""
        review = self.get_object()
        review.is_flagged = False
        review.save(update_fields=["is_flagged"])
        return Response(ReviewSerializer(review, context={"request": request}).data)
