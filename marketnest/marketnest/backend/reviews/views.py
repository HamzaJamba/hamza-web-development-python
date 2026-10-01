from django.db.models import Exists, OuterRef
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from orders.models import OrderItem
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ReviewSerializer
    pagination_class = None
    filterset_fields = ["product"]

    def get_permissions(self):
        return [permissions.AllowAny()] if self.action == "list" else [permissions.IsAuthenticated()]

    def get_queryset(self):
        bought = OrderItem.objects.filter(order__customer=OuterRef("user"), product=OuterRef("product")).exclude(status="cancelled")
        qs = Review.objects.select_related("user").annotate(verified_purchase=Exists(bought))
        if self.action == "destroy":
            return qs.filter(user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        """One review per person per product: posting again edits the earlier one."""
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        review, created = Review.objects.update_or_create(
            product=ser.validated_data["product"], user=request.user,
            defaults={"rating": ser.validated_data["rating"], "comment": ser.validated_data.get("comment", "")},
        )
        review = self.get_queryset().get(pk=review.pk)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
