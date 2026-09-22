from django.urls import path
from .views import ShipmentReportView, DriverReportView, WarehouseReportView

urlpatterns = [
    path("shipments/", ShipmentReportView.as_view(), name="report-shipments"),
    path("drivers/", DriverReportView.as_view(), name="report-drivers"),
    path("warehouses/", WarehouseReportView.as_view(), name="report-warehouses"),
]
