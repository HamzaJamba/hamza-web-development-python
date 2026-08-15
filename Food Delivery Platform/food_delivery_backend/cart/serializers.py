from rest_framework import serializers
from menu.models import FoodItem
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source="food_item.name", read_only=True)
    unit_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id", "food_item", "food_item_name", "quantity",
            "special_instructions", "unit_price", "line_total",
        )
        read_only_fields = ("id",)

    def get_unit_price(self, obj):
        return obj.food_item.discount_price or obj.food_item.price

    def get_line_total(self, obj):
        return obj.line_total


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "restaurant", "restaurant_name", "items", "subtotal", "updated_at")
        read_only_fields = ("id", "restaurant", "updated_at")

    def get_subtotal(self, obj):
        return obj.subtotal


class AddToCartSerializer(serializers.Serializer):
    """Adds an item; if the cart already has items from a *different* restaurant,
    caller must confirm clearing the cart first (mirrors real food-delivery UX)."""

    food_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=255)
    replace_cart = serializers.BooleanField(required=False, default=False)

    def validate_food_item_id(self, value):
        try:
            self._food_item = FoodItem.objects.select_related("restaurant").get(id=value, is_available=True)
        except FoodItem.DoesNotExist:
            raise serializers.ValidationError("Food item not found or unavailable.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        food_item = self._food_item
        cart, _ = Cart.objects.get_or_create(customer=user)

        if cart.restaurant_id and cart.restaurant_id != food_item.restaurant_id:
            if not self.validated_data.get("replace_cart"):
                raise serializers.ValidationError(
                    {"detail": "Cart has items from another restaurant.", "code": "DIFFERENT_RESTAURANT"}
                )
            cart.items.all().delete()

        cart.restaurant = food_item.restaurant
        cart.save(update_fields=["restaurant"])

        item, created = CartItem.objects.get_or_create(
            cart=cart, food_item=food_item,
            defaults={
                "quantity": self.validated_data["quantity"],
                "special_instructions": self.validated_data.get("special_instructions", ""),
            },
        )
        if not created:
            item.quantity += self.validated_data["quantity"]
            item.save(update_fields=["quantity"])
        return cart
