from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services as svc

PARAMS = [OpenApiParameter("plant", int), OpenApiParameter("months", int)]


class _Base(APIView):
    # read-only for any authenticated user (default RoleBasedPermission)
    @staticmethod
    def p(request):
        plant = request.query_params.get("plant")
        months = max(1, min(int(request.query_params.get("months", 6)), 24))
        return (int(plant) if plant else None), months


@extend_schema(parameters=PARAMS, responses=dict)
class OverviewView(_Base):
    def get(self, request):
        plant, _ = self.p(request)
        return Response(svc.overview(plant))


@extend_schema(parameters=PARAMS, responses=dict)
class EquipmentHealthView(_Base):
    def get(self, request):
        plant, _ = self.p(request)
        return Response(svc.equipment_health(plant))


@extend_schema(parameters=PARAMS, responses=dict)
class DowntimeView(_Base):
    def get(self, request):
        plant, months = self.p(request)
        return Response(svc.downtime(months, plant))


@extend_schema(parameters=PARAMS, responses=dict)
class MaintenanceCostView(_Base):
    def get(self, request):
        plant, months = self.p(request)
        return Response(svc.maintenance_cost(months, plant))


@extend_schema(parameters=PARAMS, responses=dict)
class IncidentStatsView(_Base):
    def get(self, request):
        plant, months = self.p(request)
        return Response(svc.incident_stats(months, plant))


@extend_schema(parameters=PARAMS, responses=dict)
class InventoryUsageView(_Base):
    def get(self, request):
        _, months = self.p(request)
        return Response(svc.inventory_usage(months))


@extend_schema(parameters=PARAMS, responses=dict)
class EmployeePerformanceView(_Base):
    def get(self, request):
        plant, _ = self.p(request)
        return Response(svc.employee_performance(plant=plant))
