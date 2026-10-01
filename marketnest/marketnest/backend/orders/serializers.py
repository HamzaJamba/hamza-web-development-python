from rest_framework import serializers
from catalog.models import Product
from .models import Order, OrderItem


class CheckoutLineSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=20)


class CheckoutSerializer(serializers.Serializer):
    items = CheckoutLineSerializer(many=True, allow_empty=False)
    full_name = serializers.CharField(max_length=120)
    phone = serializers.RegexField(r"^[0-9+\-\s]{7,20}$", error_messages={"invalid": "Enter a valid phone number."})
    address = serializers.CharField(max_length=300)
    city = serializers.CharField(max_length=80)
    payment_method = serializers.ChoiceField(choices=["cod", "card"])
    card_number = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate(self, data):
        if data["payment_method"] == "card" and not data.get("card_number"):
            raise serializers.ValidationError({"card_number": "Enter your card number."})
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.CharField(source="product.slug", read_only=True, default=None)
    hue = serializers.IntegerField(source="product.hue", read_only=True, default=200)
    image_url = serializers.CharField(source="product.image_url", read_only=True, default="")
    category_icon = serializers.CharField(source="product.category.icon", read_only=True, default="Package")
    vendor_name = serializers.CharField(source="vendor.shop_name", read_only=True)
    vendor_slug = serializers.CharField(source="vendor.slug", read_only=True)
    awning_primary = serializers.CharField(source="vendor.awning_primary", read_only=True)
    awning_secondary = serializers.CharField(source="vendor.awning_secondary", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_slug", "product_name", "hue", "image_url", "category_icon",
            "vendor_name", "vendor_slug", "awning_primary", "awning_secondary",
            "unit_price", "quantity", "line_total", "status", "status_label",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "number", "status", "status_label", "payment_method", "payment_status",
            "subtotal", "shipping_fee", "total", "full_name", "phone", "address", "city",
            "created_at", "items",
        ]


class VendorItemSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    order_date = serializers.DateTimeField(source="order.created_at", read_only=True)
    customer_name = serializers.CharField(source="order.full_name", read_only=True)
    city = serializers.CharField(source="order.city", read_only=True)
    address = serializers.CharField(source="order.address", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    next_statuses = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "order_number", "order_date", "customer_name", "city", "address",
            "product_name", "unit_price", "quantity", "line_total", "commission",
            "status", "status_label", "next_statuses",
        ]

    def get_next_statuses(self, obj):
        return OrderItem.TRANSITIONS.get(obj.status, [])
