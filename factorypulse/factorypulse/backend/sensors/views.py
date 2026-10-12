from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SensorReading
from .serializers import SensorReadingSerializer
from .ml import score_reading


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().select_related("machine")
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["machine", "is_anomaly"]
    ordering_fields = ["recorded_at"]

    def perform_create(self, serializer):
        data = serializer.validated_data
        machine = data["machine"]
        is_anomaly, score = score_reading(machine, float(data["vibration_mm_s"]), float(data["temperature_c"]),
                                           float(data["pressure_bar"]), int(data["rpm"]))
        reading = serializer.save(is_anomaly=is_anomaly, anomaly_score=score)

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(f"machine_{machine.id}", {"type": "sensor.update", "data": SensorReadingSerializer(reading).data})
            async_to_sync(channel_layer.group_send)("plant_overview", {"type": "sensor.update", "data": SensorReadingSerializer(reading).data})
        return reading
