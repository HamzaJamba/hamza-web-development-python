from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsRider
from dashboard.models import PlatformSettings
from notifications.models import Notification
from orders.models import Order
from .models import Rider, Delivery
from .serializers import RiderSerializer, RiderLocationUpdateSerializer, DeliverySerializer, RiderCnicReviewSerializer


class MyRiderProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/riders/me/ — vehicle info, and used by the frontend to read online status."""

    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated, IsRider]

    def get_object(self):
        rider, _ = Rider.objects.get_or_create(user=self.request.user)
        return rider


class ToggleOnlineView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsRider]

    def post(self, request):
        rider, _ = Rider.objects.get_or_create(user=request.user)
        if not rider.is_online and rider.cnic_status != Rider.CnicStatus.VERIFIED:
            return Response(
                {"detail": "Your CNIC must be verified by an admin before you can go online.", "cnic_status": rider.cnic_status},
                status=status.HTTP_403_FORBIDDEN,
            )
        rider.is_online = not rider.is_online
        rider.save(update_fields=["is_online"])
        return Response({"is_online": rider.is_online})


class UpdateLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsRider]

    def post(self, request):
        serializer = RiderLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rider, _ = Rider.objects.get_or_create(user=request.user)
        rider.current_latitude = serializer.validated_data["latitude"]
        rider.current_longitude = serializer.validated_data["longitude"]
        rider.save(update_fields=["current_latitude", "current_longitude"])
        return Response(RiderSerializer(rider).data)


class AvailableDeliveriesView(generics.ListAPIView):
    """GET /api/riders/deliveries/available/ — unassigned deliveries for READY_FOR_PICKUP orders."""

    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsRider]

    def get_queryset(self):
        return Delivery.objects.filter(rider__isnull=True, order__status=Order.Status.READY_FOR_PICKUP)


class MyDeliveriesView(generics.ListAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsRider]

    def get_queryset(self):
        return Delivery.objects.filter(rider__user=self.request.user)


class AcceptDeliveryView(APIView):
    """POST /api/riders/deliveries/{id}/accept/ — rider claims an available delivery."""

    permission_classes = [permissions.IsAuthenticated, IsRider]

    @transaction.atomic
    def post(self, request, pk):
        rider, _ = Rider.objects.get_or_create(user=request.user)
        delivery = Delivery.objects.select_for_update().get(id=pk, rider__isnull=True)
        delivery.rider = rider
        delivery.save(update_fields=["rider"])

        order = delivery.order
        order.status = Order.Status.OUT_FOR_DELIVERY
        order.save(update_fields=["status"])

        Notification.objects.create(
            recipient=order.customer,
            type=Notification.Type.RIDER_ASSIGNED,
            title="Rider assigned",
            message=f"{rider.user.username} is on the way with order {order.order_number}.",
            related_order_id=order.id,
        )
        return Response(DeliverySerializer(delivery).data)


class UpdateDeliveryStatusView(APIView):
    """POST /api/riders/deliveries/{id}/status/  {status: PICKED_UP|DELIVERED|FAILED}"""

    permission_classes = [permissions.IsAuthenticated, IsRider]

    @transaction.atomic
    def post(self, request, pk):
        delivery = Delivery.objects.get(id=pk, rider__user=request.user)
        new_status = request.data.get("status")
        if new_status not in (Delivery.Status.PICKED_UP, Delivery.Status.DELIVERED, Delivery.Status.FAILED):
            return Response({"status": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        delivery.status = new_status
        now = timezone.now()
        if new_status == Delivery.Status.PICKED_UP:
            delivery.picked_up_at = now
        elif new_status == Delivery.Status.DELIVERED:
            delivery_fee = Decimal(str(PlatformSettings.load().rider_delivery_fee))
            delivery.delivered_at = now
            delivery.delivery_fee_earned = delivery_fee
            delivery.order.status = Order.Status.COMPLETED
            delivery.order.completed_at = now
            delivery.order.save(update_fields=["status", "completed_at"])

            rider = delivery.rider
            rider.total_earnings += delivery_fee
            rider.total_deliveries += 1
            rider.save(update_fields=["total_earnings", "total_deliveries"])

            Notification.objects.create(
                recipient=delivery.order.customer,
                type=Notification.Type.DELIVERED,
                title="Delivered!",
                message=f"Order {delivery.order.order_number} has been delivered. Bon appetit!",
                related_order_id=delivery.order.id,
            )
        delivery.save()
        return Response(DeliverySerializer(delivery).data)


class AdminListRidersView(generics.ListAPIView):
    """GET /api/riders/admin/list/?cnic_status=PENDING — admin view of all riders, filterable by CNIC status."""

    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = Rider.objects.select_related("user").all()
        cnic_status = self.request.query_params.get("cnic_status")
        if cnic_status:
            qs = qs.filter(cnic_status=cnic_status)
        return qs


class AdminReviewCnicView(APIView):
    """POST /api/riders/admin/{rider_id}/review-cnic/  {action: 'verify'|'reject', reason}"""

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, rider_id):
        rider = Rider.objects.get(id=rider_id)
        serializer = RiderCnicReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["action"] == "verify":
            rider.cnic_status = Rider.CnicStatus.VERIFIED
            rider.cnic_rejection_reason = ""
        else:
            rider.cnic_status = Rider.CnicStatus.REJECTED
            rider.cnic_rejection_reason = serializer.validated_data.get("reason", "")
            rider.is_online = False  # can't stay online with a rejected CNIC

        rider.save(update_fields=["cnic_status", "cnic_rejection_reason", "is_online"])

        Notification.objects.create(
            recipient=rider.user,
            type=Notification.Type.SYSTEM,
            title="CNIC verification update",
            message=(
                "Your CNIC has been verified — you can now go online."
                if rider.cnic_status == Rider.CnicStatus.VERIFIED
                else f"Your CNIC was rejected: {rider.cnic_rejection_reason or 'please resubmit.'}"
            ),
        )
        return Response(RiderSerializer(rider).data)
