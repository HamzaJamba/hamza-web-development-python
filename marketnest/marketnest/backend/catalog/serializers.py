from rest_framework import serializers
from vendors.serializers import VendorMiniSerializer
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "hue", "product_count"]


class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "hue"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    vendor = VendorMiniSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "name", "description", "price", "compare_at_price", "stock",
            "image_url", "hue", "rating_avg", "rating_count", "sold_count", "is_active",
            "category", "category_id", "vendor", "created_at",
        ]
        read_only_fields = ["slug", "rating_avg", "rating_count", "sold_count", "created_at"]

    def validate(self, data):
        price = data.get("price", getattr(self.instance, "price", None))
        compare = data.get("compare_at_price", getattr(self.instance, "compare_at_price", None))
        if compare is not None and price is not None and compare <= price:
            raise serializers.ValidationError({"compare_at_price": "Original price must be higher than the selling price."})
        return data
