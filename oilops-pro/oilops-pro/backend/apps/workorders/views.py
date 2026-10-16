import django_filters as df
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin
from apps.audit.services import log_action

from . import serializers as s
from . import services
from .models import WorkOrder

MGMT = [Role.PLANT_MANAGER, Role.ENGINEER]
FIELD = MGMT + [Role.TECHNICIAN]


class WorkOrderFilter(df.FilterSet):
    plant = df.NumberFilter(field_name="equipment__plant")
    technician = df.NumberFilter(field_name="technicians")
    overdue = df.BooleanFilter(method="f_overdue")
    assigned_to_me = df.BooleanFilter(method="f_mine")
    deadline_before = df.IsoDateTimeFilter(field_name="deadline", lookup_expr="lte")

    class Meta:
        model = WorkOrder
        fields = ["status", "priority", "wo_type", "equipment", "engineer"]

    def f_overdue(self, qs, name, value):
        cond = Q(deadline__lt=timezone.now(), status__in=WorkOrder.OPEN_STATUSES)
        return qs.filter(cond) if value else qs.exclude(cond)

    def f_mine(self, qs, name, value):
        u = self.request.user
        return qs.filter(Q(technicians=u) | Q(engineer=u)).distinct() if value else qs


class WorkOrderViewSet(AuditMixin, viewsets.ModelViewSet):
    write_roles = MGMT
    action_roles = {"start": FIELD, "hold": FIELD, "complete": FIELD, "add_part": FIELD,
                    "assign": MGMT, "cancel": MGMT}
    filterset_class = WorkOrderFilter
    search_fields = ["number", "title", "equipment__name", "equipment__serial_number"]
    ordering_fields = ["created_at", "deadline", "priority", "status"]

    def get_queryset(self):
        return (WorkOrder.objects.select_related("equipment", "equipment__plant", "engineer", "created_by")
                .prefetch_related("technicians", "parts__item"))

    def get_serializer_class(self):
        return s.WorkOrderDetailSerializer if self.action == "retrieve" else s.WorkOrderSerializer

    def _act(self, wo, name):
        log_action(self.request.user, name.upper(), "WorkOrder", wo.pk, wo, {"status": wo.status}, self.request)
        return Response(s.WorkOrderDetailSerializer(wo, context=self.get_serializer_context()).data)

    @extend_schema(request=s.AssignSerializer, responses=s.WorkOrderDetailSerializer)
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        d = s.AssignSerializer(data=request.data)
        d.is_valid(raise_exception=True)
        wo = services.assign(self.get_object(), d.validated_data.get("engineer"), d.validated_data.get("technicians"), request.user)
        return self._act(wo, "assign")

    @extend_schema(request=None, responses=s.WorkOrderDetailSerializer)
    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        return self._act(services.start(self.get_object(), request.user), "start")

    @extend_schema(request=s.ReasonSerializer, responses=s.WorkOrderDetailSerializer)
    @action(detail=True, methods=["post"])
    def hold(self, request, pk=None):
        return self._act(services.hold(self.get_object(), request.user, request.data.get("reason", "")), "hold")

    @extend_schema(request=s.CompleteSerializer, responses=s.WorkOrderDetailSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        d = s.CompleteSerializer(data=request.data)
        d.is_valid(raise_exception=True)
        v = d.validated_data
        wo = services.complete(self.get_object(), request.user, v["completion_notes"], v.get("labor_hours"), v.get("downtime_hours"))
        return self._act(wo, "complete")

    @extend_schema(request=s.ReasonSerializer, responses=s.WorkOrderDetailSerializer)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._act(services.cancel(self.get_object(), request.user, request.data.get("reason", "")), "cancel")

    @extend_schema(request=s.AddPartSerializer, responses=s.SparePartUsageSerializer)
    @action(detail=True, methods=["post"], url_path="parts")
    def add_part(self, request, pk=None):
        d = s.AddPartSerializer(data=request.data)
        d.is_valid(raise_exception=True)
        usage = services.add_part(self.get_object(), d.validated_data["item"], d.validated_data["quantity"], request.user)
        return Response(s.SparePartUsageSerializer(usage).data, status=201)
