from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    AddressViewSet,
    AdminUserViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SendEmailVerificationView,
    ConfirmEmailVerificationView,
)

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="address")
router.register("admin/users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("verify-email/", SendEmailVerificationView.as_view(), name="verify-email"),
    path("verify-email/confirm/", ConfirmEmailVerificationView.as_view(), name="verify-email-confirm"),
    path("", include(router.urls)),
]
