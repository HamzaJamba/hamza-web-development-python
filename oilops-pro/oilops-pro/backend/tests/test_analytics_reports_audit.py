from datetime import timedelta

import pytest
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.incidents.models import Incident
from apps.workorders.models import WorkOrder

pytestmark = pytest.mark.django_db


@pytest.fixture
def data(pump, plant, users):
    now = timezone.now()
    wo = WorkOrder.objects.create(title="Done", equipment=pump, wo_type="EMERGENCY", status="COMPLETED", completed_at=now,
                                  deadline=now + timedelta(days=1), labor_hours=4, downtime_hours=6, engineer=users["ENGINEER"])
    wo.technicians.add(users["TECHNICIAN"])
    Incident.objects.create(title="Fire drill gone wrong", incident_type="FIRE", severity="MAJOR", plant=plant, description="d",
                            downtime_hours=10, injuries=1, estimated_loss=5000, occurred_at=now)


@pytest.mark.parametrize("path", ["overview", "equipment-health", "downtime", "maintenance-cost", "incidents",
                                  "inventory-usage", "employee-performance"])
def test_analytics_endpoints_ok(api, data, path):
    r = api("VIEWER").get(f"/api/v1/analytics/{path}/")
    assert r.status_code == 200


def test_analytics_values(api, data):
    c = api("VIEWER")
    assert c.get("/api/v1/analytics/overview/").data["equipment_total"] == 1
    assert c.get("/api/v1/analytics/downtime/").data["total_hours"] == 16
    assert c.get("/api/v1/analytics/maintenance-cost/").data["total"] == 140
    perf = c.get("/api/v1/analytics/employee-performance/").data
    assert {p["role"] for p in perf} == {"ENGINEER", "TECHNICIAN"} and all(p["on_time_pct"] == 100 for p in perf)
    assert c.get("/api/v1/analytics/incidents/").data["injuries"] == 1


@pytest.mark.parametrize("name", ["maintenance", "incidents", "equipment", "monthly-performance"])
def test_report_json_pdf_xlsx(api, data, name):
    c = api("PLANT_MANAGER")
    assert c.get(f"/api/v1/reports/{name}/").data["title"]
    pdf = c.get(f"/api/v1/reports/{name}/?export=pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    xl = c.get(f"/api/v1/reports/{name}/?export=xlsx")
    assert xl.status_code == 200 and xl.content[:2] == b"PK"


def test_report_errors(api):
    c = api("PLANT_MANAGER")
    assert c.get("/api/v1/reports/nope/").status_code == 404
    assert c.get("/api/v1/reports/maintenance/?export=docx").status_code == 400
    assert c.get("/api/v1/reports/maintenance/?date_from=garbage").status_code == 400


def test_audit_trail_records_changes(api, pump, users):
    c = api("ENGINEER")
    c.patch(f"/api/v1/equipment/{pump.pk}/", {"name": "Pump P-1 (renamed)"}, format="json")
    c.delete(f"/api/v1/equipment/{pump.pk}/")
    upd = AuditLog.objects.get(action="UPDATE", model="Equipment")
    assert upd.changes["name"]["to"] == "Pump P-1 (renamed)" and upd.user == users["ENGINEER"]
    assert AuditLog.objects.filter(action="DELETE", model="Equipment").exists()
    assert api("ADMIN").get("/api/v1/audit/logs/?model=Equipment").data["count"] == 2


def test_report_export_is_audited(api, data):
    api("PLANT_MANAGER").get("/api/v1/reports/equipment/?export=pdf")
    assert AuditLog.objects.filter(action="EXPORT").count() == 1
