from rest_framework import serializers
from .models import Room, RoomImage, RoomAvailability


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image']


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'hotel_name', 'title', 'description', 'bed_type',
            'price_per_night', 'max_guests', 'has_wifi', 'has_ac', 'has_tv',
            'has_balcony', 'is_available', 'images', 'created_at',
        ]


class RoomAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAvailability
        fields = ['id', 'room', 'date', 'is_blocked']
