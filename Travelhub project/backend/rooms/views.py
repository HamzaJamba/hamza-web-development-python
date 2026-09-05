from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from common.permissions import IsHotelOwner
from .models import Room, RoomAvailability
from .serializers import RoomSerializer, RoomAvailabilitySerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(is_available=True)
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hotel', 'bed_type', 'max_guests']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsHotelOwner()]
        return [permissions.AllowAny()]


class RoomAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = RoomAvailability.objects.all()
    serializer_class = RoomAvailabilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'date']
    permission_classes = [permissions.IsAuthenticated, IsHotelOwner]
