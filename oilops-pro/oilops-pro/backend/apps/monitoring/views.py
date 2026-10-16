from datetime import timedelta

import django_filters as df
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from .auth import DeviceKeyAuthentication
from .models import METRIC_UNITS, Alert, Metric, SensorReading, Threshold
from .serializers import AlertSerializer, SensorReadingSerializer, ThresholdSerializer
from .services import applicable_thresholds, ingest_reading, recompute_health
from rest_framework_simplejwt.authentication import JWTAuthentication

FIELD = [Role.TECHNICIAN, Role.ENGINEER, Role.PLANT_MANAGER]


class ReadingFilter(df.FilterSet):
    since = df.IsoDateTimeFilter(field_name="recorded_at", lookup_expr="gte")
    until = df.IsoDateTimeFilter(field_name="recorded_at", lookup_expr="lte")

    class Meta:
        model = SensorReading
        fields = ["equipment", "metric"]


class SensorReadingViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Telemetry ingest (JWT or X-Device-Key; single object or list) and queries."""
    queryset = SensorReading.objects.select_related("equipment")
    serializer_class = SensorReadingSerializer
    authentication_classes = [JWTAuthentication, DeviceKeyAuthentication]
    write_roles = FIELD + ["DEVICE"]
    filterset_class = ReadingFilter
    ordering_fields = ["recorded_at"]
    throttle_scope = "ingest"

    def get_serializer(self, *args, **kwargs):
        if self.action == "create" and isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        items = s.validated_data if isinstance(s.validated_data, list) else [s.validated_data]
        if len(items) > 500:
            return Response({"detail": "Maximum 500 readings per request."}, status=400)
        results, alerts = [], 0
        for it in items:
            reading, alert = ingest_reading(it["equipment"], it["metric"], it["value"], it.get("recorded_at"))
            alerts += 1 if alert else 0
            results.append(reading.pk)
        return Response({"accepted": len(results), "alerts_raised_or_updated": alerts}, status=status.HTTP_201_CREATED)

    @extend_schema(parameters=[OpenApiParameter("equipment", int, required=True)])
    @action(detail=False, methods=["get"], pagination_class=None)
    def latest(self, request):
        """Latest value per metric for one equipment, with state vs thresholds."""
        from apps.equipment.models import Equipment
        eq = Equipment.objects.filter(pk=request.query_params.get("equipment")).first()
        if not eq:
            return Response({"detail": "equipment query parameter is required."}, status=400)
        out = []
        for metric in Metric.values:
            r = SensorReading.objects.filter(equipment=eq, metric=metric).order_by("-recorded_at").first()
            if not r:
                continue
            ths = applicable_thresholds(eq, metric)
            state = "NORMAL"
            for t in ths:
                if t.breached_by(r.value) and (state == "NORMAL" or t.severity == "CRITICAL"):
                    state = t.severity
            out.append({"metric": metric, "unit": METRIC_UNITS[metric], "value": r.value, "recorded_at": r.recorded_at,
                        "state": state,
                        "limits": [{"severity": t.severity, "min": t.min_value, "max": t.max_value} for t in ths]})
        return Response(out)

    @extend_schema(parameters=[OpenApiParameter("equipment", int, required=True), OpenApiParameter("metric", str, required=True),
                               OpenApiParameter("hours", int)])
    @action(detail=False, methods=["get"], pagination_class=None)
    def series(self, request):
        hours = min(int(request.query_params.get("hours", 24)), 24 * 30)
        qs = SensorReading.objects.filter(
            equipment=request.query_params.get("equipment"), metric=request.query_params.get("metric"),
            recorded_at__gte=timezone.now() - timedelta(hours=hours)).order_by("recorded_at")[:1000]
        return Response([{"t": r.recorded_at, "v": r.value} for r in qs])


class AlertViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Alert.objects.select_related("equipment", "equipment__plant")
    serializer_class = AlertSerializer
    action_roles = {"acknowledge": FIELD, "resolve": FIELD}
    filterset_fields = ["status", "severity", "equipment", "metric", "equipment__plant"]
    ordering_fields = ["created_at", "severity"]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        a = self.get_object()
        if a.status == "OPEN":
            a.status, a.acknowledged_by, a.acknowledged_at = "ACKNOWLEDGED", request.user, timezone.now()
            a.save()
        return Response(self.get_serializer(a).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        a = self.get_object()
        if a.status != "RESOLVED":
            a.status, a.resolved_at = "RESOLVED", timezone.now()
            a.save()
            recompute_health(a.equipment)
        return Response(self.get_serializer(a).data)


class ThresholdViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Threshold.objects.select_related("equipment")
    serializer_class = ThresholdSerializer
    write_roles = [Role.ENGINEER, Role.PLANT_MANAGER]
    filterset_fields = ["equipment", "category", "metric", "severity", "is_active"]
