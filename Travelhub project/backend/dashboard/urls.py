from django.urls import path
from .views import (
    AdminDashboardView, HotelOwnerDashboardView,
    TourOperatorDashboardView, CustomerDashboardView,
)

urlpatterns = [
    path('admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
    path('hotel-owner/', HotelOwnerDashboardView.as_view(), name='dashboard-hotel-owner'),
    path('tour-operator/', TourOperatorDashboardView.as_view(), name='dashboard-tour-operator'),
    path('customer/', CustomerDashboardView.as_view(), name='dashboard-customer'),
]
