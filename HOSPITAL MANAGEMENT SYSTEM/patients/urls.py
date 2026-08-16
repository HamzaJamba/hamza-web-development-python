from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("", views.PatientListView.as_view(), name="list"),
    path("add/", views.PatientCreateView.as_view(), name="add"),
    path("<int:pk>/", views.PatientDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.PatientUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.PatientDeleteView.as_view(), name="delete"),
    path("<int:patient_id>/medical-history/add/", views.MedicalHistoryCreateView.as_view(), name="medical_history_add"),
]
