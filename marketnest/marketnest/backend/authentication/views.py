from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    EmailVerifySerializer,
)
from .utils import (
    email_verification_token,
    password_reset_token,
    build_uid_token,
    decode_uid,
    send_verification_email,
    send_password_reset_email,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        uidb64, token = build_uid_token(user, email_verification_token)
        send_verification_email(user, uidb64, token)
        return Response(
            {"message": "Registered successfully. Check your email to verify your account."},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid or missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Password changed successfully."})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "forgot_password"

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            uidb64, token = build_uid_token(user, password_reset_token)
            send_password_reset_email(user, uidb64, token)
        # Always return generic success, don't reveal if email exists
        return Response({"message": "If that email exists, a reset link has been sent."})


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            uid = decode_uid(data["uidb64"])
            user = get_object_or_404(User, pk=uid)
        except Exception:
            return Response({"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not password_reset_token.check_token(user, data["token"]):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data["new_password"])
        user.save()
        return Response({"message": "Password reset successful."})


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            uid = decode_uid(data["uidb64"])
            user = get_object_or_404(User, pk=uid)
        except Exception:
            return Response({"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not email_verification_token.check_token(user, data["token"]):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()
        return Response({"message": "Email verified successfully."})
