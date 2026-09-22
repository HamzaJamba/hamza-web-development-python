import csv
import io
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import permissions

from shipments.models import Shipment
from drivers.models import Driver
from warehouses.models import Warehouse


def _period_range(period):
    today = timezone.now().date()
    if period == "daily":
        return today, today
    if period == "weekly":
        return today - timedelta(days=7), today
    if period == "monthly":
        return today - timedelta(days=30), today
    return today - timedelta(days=30), today


class BaseReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    report_name = "report"

    def get_rows(self, request):
        raise NotImplementedError

    def get(self, request):
        export_format = request.query_params.get("format", "csv")
        rows, headers = self.get_rows(request)

        if export_format == "csv":
            return self._as_csv(rows, headers)
        elif export_format == "excel":
            return self._as_excel(rows, headers)
        elif export_format == "pdf":
            return self._as_pdf(rows, headers)
        return HttpResponse("Unsupported format. Use csv, excel, or pdf.", status=400)

    def _as_csv(self, rows, headers):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.report_name}.csv"'
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(rows)
        return response

    def _as_excel(self, rows, headers):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = self.report_name[:31]
        ws.append(headers)
        for row in rows:
            ws.append(row)
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{self.report_name}.xlsx"'
        return response

    def _as_pdf(self, rows, headers):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        table_data = [headers] + [[str(c) for c in row] for row in rows]
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        doc.build([table])
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{self.report_name}.pdf"'
        return response


class ShipmentReportView(BaseReportView):
    report_name = "shipment_report"

    def get_rows(self, request):
        period = request.query_params.get("period", "monthly")
        start, end = _period_range(period)
        qs = Shipment.objects.filter(created_at__date__range=[start, end])
        headers = ["Tracking #", "Customer", "Origin", "Destination", "Status", "Priority", "Created At"]
        rows = [
            [s.tracking_number, s.customer_name, s.origin, s.destination, s.status, s.priority, s.created_at.date()]
            for s in qs
        ]
        return rows, headers


class DriverReportView(BaseReportView):
    report_name = "driver_report"

    def get_rows(self, request):
        qs = Driver.objects.all()
        headers = ["Name", "License #", "Phone", "Assigned Vehicle", "Performance Score", "Active"]
        rows = [
            [d.full_name, d.license_number, d.phone,
             d.assigned_vehicle.vehicle_number if d.assigned_vehicle else "-",
             d.performance_score, d.is_active]
            for d in qs
        ]
        return rows, headers


class WarehouseReportView(BaseReportView):
    report_name = "warehouse_report"

    def get_rows(self, request):
        qs = Warehouse.objects.all()
        headers = ["Name", "City", "Capacity", "Manager", "Active"]
        rows = [
            [w.name, w.city, w.capacity, w.manager.email if w.manager else "-", w.is_active]
            for w in qs
        ]
        return rows, headers
