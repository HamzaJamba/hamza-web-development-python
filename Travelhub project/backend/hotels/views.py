from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from common.permissions import IsHotelOwner, IsOwnerOrAdmin
from .models import Hotel
from .serializers import HotelSerializer


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.filter(is_approved=True)
    serializer_class = HotelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city', 'country']
    search_fields = ['name', 'city', 'country']
    ordering_fields = ['rating', 'created_at']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsHotelOwner()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        # Owners/admin can see their own unapproved hotels too
        user = self.request.user
        if user.is_authenticated and user.role in ['hotel_owner', 'admin']:
            if user.role == 'admin':
                return Hotel.objects.all()
            return Hotel.objects.filter(owner=user) | Hotel.objects.filter(is_approved=True)
        return Hotel.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
