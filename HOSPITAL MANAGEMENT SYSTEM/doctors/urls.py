from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.DoctorListView.as_view(), name="list"),
    path("add/", views.DoctorCreateView.as_view(), name="add"),
    path("<int:pk>/", views.DoctorDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.DoctorUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.DoctorDeleteView.as_view(), name="delete"),
]
