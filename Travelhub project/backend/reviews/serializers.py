from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'hotel', 'tour_package', 'rating', 'comment', 'image', 'created_at']
        read_only_fields = ['user']
