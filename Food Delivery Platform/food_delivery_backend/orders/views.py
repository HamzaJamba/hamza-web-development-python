from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsCustomer, IsRestaurantOwner
from payments.models import Payment
from .models import Order, Coupon
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CheckoutSerializer,
    CancelOrderSerializer,
    OrderStatusUpdateSerializer,
    CouponSerializer,
)
from . import services


class CouponViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD: /api/orders/coupons/
    Customers validate a code for free during checkout (services.checkout handles that);
    this endpoint is purely for admin management of the coupon catalog.
    """

    queryset = Coupon.objects.all().order_by("-valid_until")
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class CheckoutView(APIView):
    """POST /api/orders/checkout/  -> creates Order + Payment from the customer's cart."""

    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    throttle_scope = "order_create"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order, payment_method = services.checkout(
            customer=request.user,
            delivery_address_id=serializer.validated_data["delivery_address_id"],
            payment_method=serializer.validated_data["payment_method"],
            coupon_code=serializer.validated_data.get("coupon_code"),
        )
        payment_status = Payment.Status.PAID if payment_method == "COD" else Payment.Status.PENDING
        Payment.objects.create(
            order=order, method=payment_method, amount=order.grand_total, status=payment_status
        )
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """
    GET /api/orders/  -> scoped by role:
      CUSTOMER          -> their own orders
      RESTAURANT_OWNER  -> orders placed at restaurants they own
      ADMIN             -> everything
    """

    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status"]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("restaurant")
        if user.role == "CUSTOMER":
            return qs.filter(customer=user)
        if user.role == "RESTAURANT_OWNER":
            return qs.filter(restaurant__owner=user)
        if user.role == "ADMIN":
            return qs
        return qs.none()


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.all()
        if user.role == "CUSTOMER":
            return qs.filter(customer=user)
        if user.role == "RESTAURANT_OWNER":
            return qs.filter(restaurant__owner=user)
        return qs  # ADMIN


class OrderStatusUpdateView(APIView):
    """POST /api/orders/{id}/status/  {status: ACCEPTED|PREPARING|...} — restaurant owner drives the kitchen flow."""

    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwner]

    def post(self, request, pk):
        order = Order.objects.get(id=pk, restaurant__owner=request.user)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.transition_status(order, serializer.validated_data["status"], actor=request.user)
        return Response(OrderDetailSerializer(order).data)


class OrderCancelView(APIView):
    """POST /api/orders/{id}/cancel/  {reason} — customer can cancel while still PENDING/ACCEPTED."""

    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def post(self, request, pk):
        order = Order.objects.get(id=pk, customer=request.user)
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.transition_status(order, Order.Status.CANCELLED, actor=request.user)
        order.cancel_reason = serializer.validated_data.get("reason", "")
        order.save(update_fields=["cancel_reason"])
        return Response(OrderDetailSerializer(order).data)
