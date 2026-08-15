from rest_framework import serializers
from .models import Category, FoodItem, FoodImage, WishlistItem, WishlistItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "icon", "is_active")
        read_only_fields = ("id",)


class FoodImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodImage
        fields = ("id", "image", "is_primary")
        read_only_fields = ("id",)


class FoodItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            "id", "name", "price", "discount_price", "category_name",
            "is_available", "avg_rating", "primary_image",
        )

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        return img.image.url if img and img.image else None


class FoodItemDetailSerializer(serializers.ModelSerializer):
    images = FoodImageSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = FoodItem
        fields = (
            "id", "restaurant", "restaurant_name", "category", "name", "description",
            "price", "discount_price", "is_available", "avg_rating", "total_reviews",
            "total_orders", "images", "created_at", "updated_at",
        )
        read_only_fields = ("id", "avg_rating", "total_reviews", "total_orders", "created_at", "updated_at")


class FoodItemWriteSerializer(serializers.ModelSerializer):
    """Owner create/update — restaurant is locked to one of the owner's own restaurants."""

    class Meta:
        model = FoodItem
        fields = (
            "id", "restaurant", "category", "name", "description",
            "price", "discount_price", "is_available",
        )
        read_only_fields = ("id",)

    def validate_restaurant(self, restaurant):
        user = self.context["request"].user
        if restaurant.owner_id != user.id:
            raise serializers.ValidationError("You can only add food items to your own restaurant.")
        return restaurant


class WishlistItemSerializer(serializers.ModelSerializer):
    food_item_detail = FoodItemListSerializer(source="food_item", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "food_item", "food_item_detail", "added_at")
        read_only_fields = ("id", "added_at")

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)


class WishlistItemSerializer(serializers.ModelSerializer):
    food_item_detail = FoodItemListSerializer(source="food_item", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "food_item", "food_item_detail", "added_at")
        read_only_fields = ("id", "added_at")

    def validate_food_item(self, food_item):
        user = self.context["request"].user
        if WishlistItem.objects.filter(customer=user, food_item=food_item).exists():
            raise serializers.ValidationError("Already in your wishlist.")
        return food_item

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)
