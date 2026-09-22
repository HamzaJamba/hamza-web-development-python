from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import GPSLog, IoTReading
from .serializers import GPSLogSerializer, IoTReadingSerializer


class GPSLogViewSet(viewsets.ModelViewSet):
    queryset = GPSLog.objects.all().select_related("vehicle")
    serializer_class = GPSLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["vehicle"]
    ordering_fields = ["recorded_at"]

    def perform_create(self, serializer):
        log = serializer.save()
        # Push live update to the vehicle's tracking WebSocket group
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"vehicle_{log.vehicle_id}",
                {
                    "type": "gps.update",
                    "data": GPSLogSerializer(log).data,
                },
            )

    def get_queryset(self):
        qs = super().get_queryset()
        vehicle_id = self.request.query_params.get("latest_for_vehicle")
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)[:1]
        return qs


class IoTReadingViewSet(viewsets.ModelViewSet):
    queryset = IoTReading.objects.all().select_related("vehicle")
    serializer_class = IoTReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["vehicle", "is_alert"]
