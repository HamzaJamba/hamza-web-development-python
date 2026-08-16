from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.AppointmentListView.as_view(), name="list"),
    path("add/", views.AppointmentCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.AppointmentUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.AppointmentDeleteView.as_view(), name="delete"),
]
