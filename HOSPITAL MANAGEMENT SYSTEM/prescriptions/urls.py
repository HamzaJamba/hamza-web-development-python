from django.urls import path
from . import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.PrescriptionListView.as_view(), name="list"),
    path("add/", views.PrescriptionCreateView.as_view(), name="add"),
    path("<int:pk>/", views.PrescriptionDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.PrescriptionUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.PrescriptionDeleteView.as_view(), name="delete"),
]
