from django.urls import path
from .views import PlantOverviewView, MachineTrendView

urlpatterns = [
    path("overview/", PlantOverviewView.as_view(), name="dashboard-overview"),
    path("machine/<uuid:pk>/trend/", MachineTrendView.as_view(), name="machine-trend"),
]
