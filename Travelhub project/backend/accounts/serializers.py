from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import OTP

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'phone', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Role.CUSTOMER),
            is_active=True,
        )
        OTP.objects.create(user=user, purpose=OTP.Purpose.REGISTRATION)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        otp = OTP.objects.filter(
            user=user, purpose=OTP.Purpose.REGISTRATION, code=attrs['code']
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            raise serializers.ValidationError('Invalid or expired OTP.')

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No account found with this email.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        otp = OTP.objects.filter(
            user=user, purpose=OTP.Purpose.PASSWORD_RESET, code=attrs['code']
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            raise serializers.ValidationError('Invalid or expired OTP.')

        attrs['user'] = user
        attrs['otp'] = otp
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'is_verified', 'is_approved', 'profile_image']
        read_only_fields = ['role', 'is_verified', 'is_approved']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError('Account not verified. Please verify OTP first.')
        if not self.user.is_approved:
            raise serializers.ValidationError('Account pending admin approval.')
        data['user'] = UserSerializer(self.user).data
        return data
