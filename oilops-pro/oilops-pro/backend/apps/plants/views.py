from django.db.models import Count
from rest_framework import viewsets

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from .models import Pipeline, Plant, StorageTank
from .serializers import PipelineSerializer, PlantSerializer, StorageTankSerializer

WRITE = [Role.PLANT_MANAGER, Role.ENGINEER]


class PlantViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = PlantSerializer
    write_roles = [Role.PLANT_MANAGER]
    filterset_fields = ["plant_type", "status", "city"]
    search_fields = ["name", "code", "city"]
    ordering_fields = ["name", "capacity_bpd", "created_at"]

    def get_queryset(self):
        return Plant.objects.select_related("manager").annotate(
            equipment_count=Count("equipment", distinct=True), tank_count=Count("tanks", distinct=True))


class PipelineViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Pipeline.objects.select_related("origin", "destination")
    serializer_class = PipelineSerializer
    write_roles = WRITE
    filterset_fields = ["status", "origin", "destination"]
    search_fields = ["name", "code", "product"]


class StorageTankViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = StorageTank.objects.select_related("plant")
    serializer_class = StorageTankSerializer
    write_roles = WRITE + [Role.TECHNICIAN]
    filterset_fields = ["plant", "product", "status"]
    search_fields = ["tag", "plant__name"]
