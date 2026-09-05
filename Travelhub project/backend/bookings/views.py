from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.permissions import IsAdmin
from .models import Booking, Coupon
from .serializers import BookingSerializer, CouponSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'booking_type']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Booking.objects.all()
        if user.role == 'hotel_owner':
            return Booking.objects.filter(room__hotel__owner=user)
        if user.role == 'tour_operator':
            return Booking.objects.filter(tour_package__operator=user)
        return Booking.objects.filter(customer=user)

    def perform_create(self, serializer):
        booking = serializer.save(customer=self.request.user)
        # Apply coupon discount if provided
        if booking.coupon_code:
            coupon = Coupon.objects.filter(code=booking.coupon_code, is_active=True).first()
            if coupon:
                discount = booking.total_price * coupon.discount_percent / 100
                booking.discount_amount = discount
                booking.total_price -= discount
                booking.save()
                coupon.used_count += 1
                coupon.save()

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
