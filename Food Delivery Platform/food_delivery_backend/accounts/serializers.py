from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Address


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "password", "password2",
            "role", "phone_number",
        )

    def validate_role(self, value):
        # Nobody can self-register as ADMIN via the public endpoint.
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("Cannot self-register as Admin.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        role = validated_data.get("role", User.Role.CUSTOMER)
        # Restaurant owners & riders need admin approval before they can operate.
        needs_approval = role in (User.Role.RESTAURANT_OWNER, User.Role.RIDER)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            phone_number=validated_data.get("phone_number", ""),
            is_approved=not needs_approval,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "role", "phone_number",
            "profile_photo", "is_email_verified", "is_approved", "created_at",
        )
        read_only_fields = ("id", "role", "is_email_verified", "is_approved", "created_at")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "label", "address_line", "city", "latitude", "longitude", "is_default")
        read_only_fields = ("id",)


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "role", "phone_number",
            "is_approved", "is_active", "is_email_verified", "created_at",
        )
        read_only_fields = fields


class AdminUserActionSerializer(serializers.Serializer):
    """Used for approve/suspend/activate admin actions — no body needed, kept for schema clarity."""
    pass


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Embeds role + id directly in the JWT so the frontend can route to the right dashboard
    without an extra /me call right after login."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["is_approved"] = user.is_approved
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["is_approved"] = self.user.is_approved
        return data
