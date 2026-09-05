import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from bookings.models import Booking
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user, transaction_id=str(uuid.uuid4())[:12])
        # Demo: cash & fake card auto-succeed; real gateways would verify via webhook
        if payment.method in [Payment.Method.CASH, Payment.Method.FAKE_CARD]:
            payment.status = Payment.Status.SUCCESS
            payment.save()
            booking = payment.booking
            booking.status = Booking.Status.CONFIRMED
            booking.save()
