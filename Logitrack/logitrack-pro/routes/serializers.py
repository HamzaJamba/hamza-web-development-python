from rest_framework import serializers
from .models import Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id", "name", "start_point", "end_point", "distance_km",
            "estimated_time_minutes", "toll_cost", "status", "created_at",
        ]
