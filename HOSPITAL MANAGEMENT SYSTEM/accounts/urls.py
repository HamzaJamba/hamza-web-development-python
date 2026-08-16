from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path("staff/add/", views.StaffCreateView.as_view(), name="staff_add"),
    path("staff/<int:pk>/edit/", views.StaffUpdateView.as_view(), name="staff_edit"),
    path("staff/<int:pk>/delete/", views.StaffDeleteView.as_view(), name="staff_delete"),
]
