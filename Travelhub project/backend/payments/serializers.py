from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'user', 'amount', 'method', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['user', 'status', 'transaction_id']
