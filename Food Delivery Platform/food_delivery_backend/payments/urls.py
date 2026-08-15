from django.urls import path
from .views import PaymentDetailView, ConfirmPaymentView

urlpatterns = [
    path("<uuid:order_id>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("<uuid:order_id>/confirm/", ConfirmPaymentView.as_view(), name="payment-confirm"),
]
