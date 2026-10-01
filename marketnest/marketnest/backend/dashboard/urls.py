from django.urls import path
from .views import VendorDashboardView, AdminDashboardView

urlpatterns = [
    path("vendor/", VendorDashboardView.as_view(), name="dashboard-vendor"),
    path("admin/", AdminDashboardView.as_view(), name="dashboard-admin"),
]
