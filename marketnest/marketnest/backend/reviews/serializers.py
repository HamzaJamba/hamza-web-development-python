from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    verified_purchase = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Review
        fields = ["id", "product", "user_name", "rating", "comment", "verified_purchase", "created_at"]

    def get_user_name(self, obj):
        u = obj.user
        return (u.full_name or u.email.split("@")[0]).strip()
