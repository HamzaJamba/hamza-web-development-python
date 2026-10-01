import re
from rest_framework import serializers
from .models import Vendor

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class VendorMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "slug", "shop_name", "awning_primary", "awning_secondary"]


class VendorSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    rating_avg = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            "id", "slug", "shop_name", "tagline", "description", "city",
            "awning_primary", "awning_secondary", "is_approved",
            "product_count", "rating_avg", "created_at",
        ]
        read_only_fields = ["slug", "is_approved", "created_at"]

    def get_product_count(self, obj):
        if hasattr(obj, "product_count"):
            return obj.product_count
        return obj.products.filter(is_active=True).count()

    def get_rating_avg(self, obj):
        val = getattr(obj, "rating_calc", None)
        return round(float(val), 2) if val else 0

    def validate_awning_primary(self, v):
        if not HEX.match(v):
            raise serializers.ValidationError("Use a hex colour like #2C3BE6.")
        return v

    validate_awning_secondary = validate_awning_primary
