from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from vendors.permissions import IsApprovedVendor
from .models import Order, OrderItem
from .serializers import CheckoutSerializer, OrderSerializer, VendorItemSerializer
from .services import create_order, restock_item, PaymentDeclined


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (Order.objects.filter(customer=self.request.user)
                .prefetch_related("items__vendor", "items__product__category"))

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            order = create_order(request.user, ser.validated_data)
        except PaymentDeclined as exc:
            return Response({"detail": exc.message, "code": "payment_declined"}, status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        with transaction.atomic():
            items = list(order.items.select_for_update())
            if any(i.status != OrderItem.PENDING for i in items):
                return Response({"detail": "A stall has already packed part of this order, so it can no longer be cancelled."},
                                status=status.HTTP_400_BAD_REQUEST)
            for i in items:
                restock_item(i)
                i.status = OrderItem.CANCELLED
                i.save(update_fields=["status"])
            if order.payment_status == "paid":
                order.payment_status = "refunded"
                from payments.models import Payment
                Payment.objects.filter(order=order).update(status=Payment.REFUNDED)
            order.refresh_status()
        return Response(OrderSerializer(order).data)


class VendorItemsView(generics.ListAPIView):
    """Order lines that belong to the signed-in vendor's stall."""
    serializer_class = VendorItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsApprovedVendor]
    filterset_fields = ["status"]

    def get_queryset(self):
        return (OrderItem.objects.filter(vendor__owner=self.request.user)
                .select_related("order").order_by("-order__created_at", "-id"))


class VendorItemStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedVendor]

    def post(self, request, pk):
        item = get_object_or_404(OrderItem, pk=pk, vendor__owner=request.user)
        new = request.data.get("status")
        if new not in OrderItem.TRANSITIONS.get(item.status, []):
            return Response({"detail": f"An item that is '{item.get_status_display()}' cannot move to '{new}'."},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            if new == OrderItem.CANCELLED:
                restock_item(item)
            item.status = new
            item.save(update_fields=["status"])
            item.order.refresh_status()
        return Response(VendorItemSerializer(item).data)
