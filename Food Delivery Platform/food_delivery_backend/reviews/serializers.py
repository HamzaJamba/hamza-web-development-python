from rest_framework import serializers
from orders.models import Order
from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ("id", "image")
        read_only_fields = ("id",)


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source="customer.username", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id", "customer", "customer_username", "order", "restaurant",
            "food_item", "rating", "comment", "images", "created_at",
        )
        read_only_fields = ("id", "customer", "restaurant", "created_at")

    def validate_order(self, order):
        user = self.context["request"].user
        if order.customer_id != user.id:
            raise serializers.ValidationError("You can only review your own orders.")
        if order.status != Order.Status.COMPLETED:
            raise serializers.ValidationError("You can only review completed orders.")
        return order

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        validated_data["restaurant"] = validated_data["order"].restaurant
        return super().create(validated_data)
