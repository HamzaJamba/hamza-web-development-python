from rest_framework import serializers
from .models import TourPackage, TourImage, TourSchedule


class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ['id', 'image']


class TourScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourSchedule
        fields = ['id', 'day_number', 'title', 'description']


class TourPackageSerializer(serializers.ModelSerializer):
    images = TourImageSerializer(many=True, read_only=True)
    schedule = TourScheduleSerializer(many=True, read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = TourPackage
        fields = [
            'id', 'operator', 'operator_name', 'name', 'destination', 'description',
            'days', 'nights', 'price', 'included_services', 'excluded_services',
            'cover_image', 'video_url', 'is_approved', 'rating', 'images', 'schedule',
            'created_at',
        ]
        read_only_fields = ['operator', 'is_approved', 'rating']
