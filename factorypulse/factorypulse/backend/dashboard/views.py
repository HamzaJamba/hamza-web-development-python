from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from equipment.models import Machine
from sensors.models import SensorReading
from maintenance.models import WorkOrder


class PlantOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        machines = Machine.objects.all()
        last_24h = timezone.now() - timedelta(hours=24)

        status_counts = dict(machines.values_list("status").annotate(c=Count("id")).order_by())
        total = machines.count()
        running = status_counts.get(Machine.RUNNING, 0)

        recent = SensorReading.objects.filter(recorded_at__gte=last_24h)
        anomaly_rate = 0.0
        recent_count = recent.count()
        if recent_count:
            anomaly_rate = recent.filter(is_anomaly=True).count() / recent_count
        availability = (running / total) if total else 0
        oee = round(availability * (1 - anomaly_rate) * 100, 1)

        return Response({
            "total_machines": total,
            "status_counts": status_counts,
            "oee_percent": oee,
            "availability_percent": round(availability * 100, 1),
            "anomaly_rate_24h_percent": round(anomaly_rate * 100, 1),
            "anomalies_24h": recent.filter(is_anomaly=True).count(),
            "readings_24h": recent_count,
            "open_work_orders": WorkOrder.objects.exclude(status__in=["completed", "cancelled"]).count(),
            "critical_machines_down": machines.filter(criticality=Machine.CRITICAL, status=Machine.DOWN).count(),
            "work_orders_by_priority": dict(
                WorkOrder.objects.exclude(status__in=["completed", "cancelled"]).values_list("priority").annotate(c=Count("id")).order_by()
            ),
        })


class MachineTrendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        readings = SensorReading.objects.filter(machine_id=pk).order_by("-recorded_at")[:50]
        data = list(reversed([
            {"recorded_at": r.recorded_at, "vibration": float(r.vibration_mm_s), "temperature": float(r.temperature_c),
             "pressure": float(r.pressure_bar), "rpm": r.rpm, "is_anomaly": r.is_anomaly, "anomaly_score": r.anomaly_score}
            for r in readings
        ]))
        return Response(data)
