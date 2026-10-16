from datetime import date

from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role
from apps.audit.services import log_action

from .builders import REPORTS
from .exporters import to_pdf, to_xlsx


class ReportView(APIView):
    read_roles = [Role.PLANT_MANAGER, Role.ENGINEER, Role.SAFETY_OFFICER, Role.HR]

    @extend_schema(parameters=[
        OpenApiParameter("export", str, enum=["json", "pdf", "xlsx"]), OpenApiParameter("plant", int),
        OpenApiParameter("date_from", str), OpenApiParameter("date_to", str), OpenApiParameter("month", str)],
        responses=dict)
    def get(self, request, name):
        builder = REPORTS.get(name)
        if not builder:
            raise NotFound(f"Unknown report '{name}'. Available: {', '.join(REPORTS)}")
        try:
            report = builder(request.query_params)
        except ValueError:
            raise ValidationError("Invalid date or month. Use YYYY-MM-DD / YYYY-MM.")
        fmt = request.query_params.get("export", "json").lower()
        stamp = date.today().isoformat()
        if fmt == "json":
            return Response(report)
        if fmt not in ("pdf", "xlsx"):
            raise ValidationError("export must be json, pdf or xlsx.")
        log_action(request.user, "EXPORT", "Report", name, f"{name}.{fmt}", dict(request.query_params.items()), request)
        if fmt == "pdf":
            resp = HttpResponse(to_pdf(report), content_type="application/pdf")
        else:
            resp = HttpResponse(to_xlsx(report), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = f'attachment; filename="{name}-{stamp}.{fmt}"'
        return resp


class ReportListView(APIView):
    read_roles = ReportView.read_roles

    @extend_schema(responses=dict)
    def get(self, request):
        return Response([{"name": n, "formats": ["json", "pdf", "xlsx"]} for n in REPORTS])
