from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Address
from .permissions import IsAdmin
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    CustomTokenObtainPairSerializer,
    AdminUserListSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


class RegisterView(generics.CreateAPIView):
    """POST /api/accounts/register/  — public. Restaurant owners/riders come back pending approval."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"
    throttle_classes = [ScopedRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(user).data,
                "message": (
                    "Registered. Awaiting admin approval."
                    if not user.is_approved
                    else "Registered successfully."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/accounts/login/  -> {access, refresh, role, is_approved}"""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"
    throttle_classes = [ScopedRateThrottle]


class LogoutView(APIView):
    """POST /api/accounts/logout/  {refresh: <token>} — blacklists the refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh"])
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/accounts/profile/ — the logged-in user's own profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only user management: /api/accounts/admin/users/
    GET     ?role=RIDER|RESTAURANT_OWNER|CUSTOMER  -> filter list
    POST .../{id}/approve/    -> approve a pending Restaurant Owner / Rider
    POST .../{id}/suspend/    -> deactivate any account
    POST .../{id}/activate/   -> reactivate a suspended account
    """

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = AdminUserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filterset_fields = ["role", "is_approved", "is_active"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        user.save(update_fields=["is_approved"])
        return Response(AdminUserListSerializer(user).data)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(AdminUserListSerializer(user).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(AdminUserListSerializer(user).data)


class PasswordResetRequestView(APIView):
    """POST /api/accounts/password-reset/  {email} — emails a uid+token reset link (console backend in dev)."""

    permission_classes = [permissions.AllowAny]
    throttle_scope = "password_reset"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Frontend builds the actual reset page URL from these two values.
            send_mail(
                subject="Reset your Food Delivery password",
                message=f"Use this uid and token in the app to reset your password.\nuid: {uid}\ntoken: {token}",
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
        # Always 200 — never reveal whether an email exists in the system.
        return Response({"detail": "If that email exists, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    """POST /api/accounts/password-reset/confirm/  {uid, token, new_password}"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"detail": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password has been reset successfully."})


class SendEmailVerificationView(APIView):
    """POST /api/accounts/verify-email/  — sends a verification link to the logged-in user's email."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_email_verified:
            return Response({"detail": "Email is already verified."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        send_mail(
            subject="Verify your Food Delivery email",
            message=f"Use this uid and token in the app to verify your email.\nuid: {uid}\ntoken: {token}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({"detail": "Verification email sent."})


class ConfirmEmailVerificationView(APIView):
    """POST /api/accounts/verify-email/confirm/  {uid, token}"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid_b64 = request.data.get("uid")
        token = request.data.get("token")
        if not uid_b64 or not token:
            return Response({"detail": "uid and token are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid_b64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired verification link."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return Response({"detail": "Email verified successfully."})


class AddressViewSet(viewsets.ModelViewSet):
    """Full CRUD for the logged-in customer's saved addresses."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
