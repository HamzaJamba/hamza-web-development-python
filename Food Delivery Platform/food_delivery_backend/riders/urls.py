from django.urls import path
from .views import (
    MyRiderProfileView,
    ToggleOnlineView,
    UpdateLocationView,
    AvailableDeliveriesView,
    MyDeliveriesView,
    AcceptDeliveryView,
    UpdateDeliveryStatusView,
    AdminListRidersView,
    AdminReviewCnicView,
)

urlpatterns = [
    path("me/", MyRiderProfileView.as_view(), name="rider-me"),
    path("toggle-online/", ToggleOnlineView.as_view(), name="rider-toggle-online"),
    path("location/", UpdateLocationView.as_view(), name="rider-location"),
    path("deliveries/available/", AvailableDeliveriesView.as_view(), name="deliveries-available"),
    path("deliveries/mine/", MyDeliveriesView.as_view(), name="deliveries-mine"),
    path("deliveries/<uuid:pk>/accept/", AcceptDeliveryView.as_view(), name="delivery-accept"),
    path("deliveries/<uuid:pk>/status/", UpdateDeliveryStatusView.as_view(), name="delivery-status"),
    path("admin/list/", AdminListRidersView.as_view(), name="admin-riders-list"),
    path("admin/<uuid:rider_id>/review-cnic/", AdminReviewCnicView.as_view(), name="admin-review-cnic"),
]
