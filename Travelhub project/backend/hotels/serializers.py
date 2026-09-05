from rest_framework import serializers
from .models import Hotel, HotelImage


class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image']


class HotelSerializer(serializers.ModelSerializer):
    images = HotelImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Hotel
        fields = [
            'id', 'owner', 'owner_name', 'name', 'description', 'city', 'country',
            'address', 'latitude', 'longitude', 'facilities', 'cover_image',
            'is_approved', 'rating', 'images', 'created_at',
        ]
        read_only_fields = ['owner', 'is_approved', 'rating']
