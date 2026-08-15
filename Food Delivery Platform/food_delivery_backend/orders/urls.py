from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CheckoutView,
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    OrderCancelView,
    CouponViewSet,
)

router = DefaultRouter()
router.register("", CouponViewSet, basename="coupon")

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="order-checkout"),
    path("coupons/", include(router.urls)),
    path("", OrderListView.as_view(), name="order-list"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:pk>/status/", OrderStatusUpdateView.as_view(), name="order-status"),
    path("<uuid:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
]
