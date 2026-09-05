from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from common.permissions import IsTourOperator, IsOwnerOrAdmin
from .models import TourPackage
from .serializers import TourPackageSerializer


class TourPackageViewSet(viewsets.ModelViewSet):
    queryset = TourPackage.objects.filter(is_approved=True)
    serializer_class = TourPackageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['destination', 'days']
    search_fields = ['name', 'destination']
    ordering_fields = ['price', 'rating', 'created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsTourOperator()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ['tour_operator', 'admin']:
            if user.role == 'admin':
                return TourPackage.objects.all()
            return TourPackage.objects.filter(operator=user) | TourPackage.objects.filter(is_approved=True)
        return TourPackage.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)
