from rest_framework import serializers
from .models import Rider, Delivery


class RiderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Rider
        fields = (
            "id", "user", "username", "vehicle_type", "vehicle_number", "cnic_number",
            "cnic_status", "cnic_rejection_reason",
            "is_online", "current_latitude", "current_longitude",
            "total_earnings", "total_deliveries",
        )
        read_only_fields = ("id", "user", "cnic_status", "cnic_rejection_reason", "total_earnings", "total_deliveries")

    def update(self, instance, validated_data):
        # Submitting/changing the CNIC number resets verification back to PENDING for admin review.
        if "cnic_number" in validated_data and validated_data["cnic_number"] != instance.cnic_number:
            instance.cnic_status = Rider.CnicStatus.PENDING
            instance.cnic_rejection_reason = ""
        return super().update(instance, validated_data)


class RiderCnicReviewSerializer(serializers.Serializer):
    """Admin-only: approve or reject a rider's CNIC submission."""

    action = serializers.ChoiceField(choices=["verify", "reject"])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)


class RiderLocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class DeliverySerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    restaurant_name = serializers.CharField(source="order.restaurant.name", read_only=True)
    rider_username = serializers.CharField(source="rider.user.username", read_only=True)

    class Meta:
        model = Delivery
        fields = (
            "id", "order", "order_number", "restaurant_name", "rider", "rider_username",
            "status", "assigned_at", "picked_up_at", "delivered_at", "delivery_fee_earned",
        )
        read_only_fields = fields
