from django.urls import path

from . import views as v

urlpatterns = [
    path("overview/", v.OverviewView.as_view()),
    path("equipment-health/", v.EquipmentHealthView.as_view()),
    path("downtime/", v.DowntimeView.as_view()),
    path("maintenance-cost/", v.MaintenanceCostView.as_view()),
    path("incidents/", v.IncidentStatsView.as_view()),
    path("inventory-usage/", v.InventoryUsageView.as_view()),
    path("employee-performance/", v.EmployeePerformanceView.as_view()),
]
