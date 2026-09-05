from rest_framework import serializers
from .models import Booking, Coupon


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'booking_type', 'room', 'tour_package',
            'check_in', 'check_out', 'tour_date', 'guests',
            'guest_name', 'guest_email', 'guest_phone',
            'total_price', 'coupon_code', 'discount_amount',
            'status', 'created_at',
        ]
        read_only_fields = ['customer', 'status', 'discount_amount']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
