from rest_framework import serializers
from .models import Order, OrderItem, Coupon


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id", "food_item", "food_name_snapshot", "unit_price_snapshot",
            "quantity", "special_instructions", "line_total",
        )

    line_total = serializers.SerializerMethodField()

    def get_line_total(self, obj):
        return obj.line_total


class OrderListSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "restaurant", "restaurant_name",
            "status", "grand_total", "placed_at",
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    customer_username = serializers.CharField(source="customer.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "customer", "customer_username", "restaurant", "restaurant_name",
            "delivery_address", "coupon", "status", "subtotal", "delivery_charges", "tax",
            "discount_amount", "grand_total", "platform_commission_percent_snapshot",
            "platform_commission_amount", "restaurant_payout", "items", "placed_at", "accepted_at",
            "completed_at", "cancelled_at", "cancel_reason",
        )
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    delivery_address_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=["COD", "STRIPE", "PAYPAL"])
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ("id", "times_used")
