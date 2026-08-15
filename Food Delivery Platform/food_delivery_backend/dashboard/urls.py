from django.urls import path
from .views import AdminDashboardView, RestaurantDashboardView, PlatformSettingsView

urlpatterns = [
    path("admin/", AdminDashboardView.as_view(), name="dashboard-admin"),
    path("restaurant/", RestaurantDashboardView.as_view(), name="dashboard-restaurant"),
    path("settings/", PlatformSettingsView.as_view(), name="dashboard-settings"),
]
