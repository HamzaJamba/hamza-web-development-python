from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, VendorItemsView, VendorItemStatusView

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

urlpatterns = [
    path("vendor-items/", VendorItemsView.as_view(), name="vendor-items"),
    path("items/<int:pk>/status/", VendorItemStatusView.as_view(), name="item-status"),
] + router.urls
