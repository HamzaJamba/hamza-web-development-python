from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import OTP
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, UserSerializer, CustomTokenObtainPairSerializer,
)

User = get_user_model()


def _send_otp_email(user, otp):
    send_mail(
        subject='TravelHub - Your OTP Code',
        message=f'Your OTP code is {otp.code}. It expires in 10 minutes.',
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        otp = user.otps.filter(purpose=OTP.Purpose.REGISTRATION).latest('created_at')
        _send_otp_email(user, otp)
        return Response(
            {'message': 'Registered successfully. Please verify OTP sent to your email.'},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        otp.is_used = True
        otp.save()
        user.is_verified = True
        user.save()
        return Response({'message': 'Account verified successfully.'})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        otp = OTP.objects.create(user=user, purpose=OTP.Purpose.PASSWORD_RESET)
        _send_otp_email(user, otp)
        return Response({'message': 'OTP sent to your email for password reset.'})


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        otp.is_used = True
        otp.save()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password reset successfully.'})


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
