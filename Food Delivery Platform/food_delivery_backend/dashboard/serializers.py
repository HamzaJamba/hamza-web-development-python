from rest_framework import serializers
from .models import PlatformSettings


class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = (
            "delivery_charge", "tax_rate_percent", "rider_delivery_fee",
            "platform_commission_percent", "support_email", "support_phone", "updated_at",
        )
        read_only_fields = ("updated_at",)
