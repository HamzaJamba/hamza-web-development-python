from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer


class PaymentDetailView(generics.RetrieveAPIView):
    """GET /api/payments/{order_id}/ — customer, the restaurant owner, or admin can view."""

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "order_id"
    lookup_url_kwarg = "order_id"

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related("order")
        if user.role == "CUSTOMER":
            return qs.filter(order__customer=user)
        if user.role == "RESTAURANT_OWNER":
            return qs.filter(order__restaurant__owner=user)
        return qs


class ConfirmPaymentView(APIView):
    """
    POST /api/payments/{order_id}/confirm/  {transaction_id}
    Stand-in for a Stripe/PayPal webhook — marks a non-COD payment PAID.
    In production this would be replaced by the real gateway's signed webhook handler.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        payment = Payment.objects.get(order_id=order_id, order__customer=request.user)
        if payment.method == Payment.Method.COD:
            return Response({"detail": "COD payments are confirmed on delivery."}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = Payment.Status.PAID
        payment.transaction_id = request.data.get("transaction_id", "")
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "transaction_id", "paid_at"])
        return Response(PaymentSerializer(payment).data)
