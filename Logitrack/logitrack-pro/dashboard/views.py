from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from shipments.models import Shipment
from fleet.models import Vehicle
from drivers.models import Driver
from warehouses.models import Warehouse


class DashboardSummaryView(APIView):
    """Cards: Total Shipments, Active Vehicles, Drivers Online, Warehouses, Delayed, Today's Deliveries."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        data = {
            "total_shipments": Shipment.objects.count(),
            "active_vehicles": Vehicle.objects.filter(status=Vehicle.ON_TRIP).count(),
            "available_vehicles": Vehicle.objects.filter(status=Vehicle.AVAILABLE).count(),
            "total_drivers": Driver.objects.filter(is_active=True).count(),
            "total_warehouses": Warehouse.objects.filter(is_active=True).count(),
            "delayed_shipments": Shipment.objects.filter(
                delivery_date__lt=today
            ).exclude(status__in=[Shipment.DELIVERED, Shipment.CANCELLED]).count(),
            "todays_deliveries": Shipment.objects.filter(delivery_date=today).count(),
            "shipments_by_status": dict(
                Shipment.objects.values_list("status").annotate(c=Count("id")).order_by()
            ),
        }
        return Response(data)


class MonthlyShipmentsChartView(APIView):
    """Monthly Shipments chart data — last 12 months, grouped by month."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncMonth
        qs = (
            Shipment.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        return Response([{"month": row["month"].strftime("%Y-%m"), "count": row["count"]} for row in qs])


class DeliverySuccessRateView(APIView):
    """Delivery Success Rate chart."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = Shipment.objects.exclude(status=Shipment.DRAFT).count()
        delivered = Shipment.objects.filter(status=Shipment.DELIVERED).count()
        cancelled = Shipment.objects.filter(status=Shipment.CANCELLED).count()
        rate = round((delivered / total) * 100, 2) if total else 0
        return Response({
            "total": total, "delivered": delivered, "cancelled": cancelled, "success_rate_percent": rate,
        })


class VehicleUtilizationView(APIView):
    """Vehicle Utilization chart — % of fleet currently on trip vs available/maintenance."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = Vehicle.objects.count()
        by_status = dict(Vehicle.objects.values_list("status").annotate(c=Count("id")).order_by())
        utilization = round((by_status.get(Vehicle.ON_TRIP, 0) / total) * 100, 2) if total else 0
        return Response({"total_vehicles": total, "by_status": by_status, "utilization_percent": utilization})
