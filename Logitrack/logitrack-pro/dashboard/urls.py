from django.urls import path
from .views import (
    DashboardSummaryView, MonthlyShipmentsChartView,
    DeliverySuccessRateView, VehicleUtilizationView,
)

urlpatterns = [
    path("summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("charts/monthly-shipments/", MonthlyShipmentsChartView.as_view(), name="chart-monthly-shipments"),
    path("charts/delivery-success-rate/", DeliverySuccessRateView.as_view(), name="chart-delivery-success"),
    path("charts/vehicle-utilization/", VehicleUtilizationView.as_view(), name="chart-vehicle-utilization"),
]
