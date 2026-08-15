from rest_framework import serializers
from .models import Restaurant, WorkingHour


class WorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHour
        fields = ("id", "weekday", "opens_at", "closes_at", "is_closed")
        read_only_fields = ("id",)


class RestaurantListSerializer(serializers.ModelSerializer):
    """Lightweight — used for browse/search listing pages."""

    class Meta:
        model = Restaurant
        fields = (
            "id", "name", "slug", "logo", "cover_image", "city",
            "status", "is_open", "avg_rating", "total_reviews",
        )


class RestaurantDetailSerializer(serializers.ModelSerializer):
    working_hours = WorkingHourSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            "id", "owner", "owner_username", "name", "slug", "description",
            "logo", "cover_image", "address_line", "city", "latitude", "longitude",
            "contact_number", "status", "is_open", "avg_rating", "total_reviews",
            "working_hours", "created_at", "updated_at",
        )
        read_only_fields = ("id", "owner", "status", "avg_rating", "total_reviews", "created_at", "updated_at")


class RestaurantCreateSerializer(serializers.ModelSerializer):
    """Owner self-registers a restaurant — always starts PENDING, owner set from request.user."""

    class Meta:
        model = Restaurant
        fields = (
            "id", "name", "slug", "description", "logo", "cover_image",
            "address_line", "city", "latitude", "longitude", "contact_number",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        validated_data["status"] = Restaurant.Status.PENDING
        return super().create(validated_data)


class RestaurantApprovalSerializer(serializers.ModelSerializer):
    """Admin-only — approve/reject/suspend a restaurant."""

    class Meta:
        model = Restaurant
        fields = ("id", "status")
        read_only_fields = ("id",)
