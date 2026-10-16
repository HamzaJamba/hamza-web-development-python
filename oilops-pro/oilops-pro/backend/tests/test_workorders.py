from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.maintenance.models import MaintenanceSchedule
from apps.maintenance.tasks import generate_due_work_orders
from apps.workorders.models import WorkOrder

pytestmark = pytest.mark.django_db


def create_wo(api, pump, users, **extra):
    body = {"title": "Replace seal", "equipment": pump.pk, "wo_type": "CORRECTIVE", "priority": "HIGH",
            "engineer": users["ENGINEER"].pk, "technicians": [users["TECHNICIAN"].pk],
            "deadline": (timezone.now() + timedelta(days=2)).isoformat(), **extra}
    return api("PLANT_MANAGER").post("/api/v1/work-orders/", body, format="json")


def test_create_assigns_and_numbers(api, pump, users):
    r = create_wo(api, pump, users)
    assert r.status_code == 201, r.data
    assert r.data["number"].startswith("WO-") and r.data["status"] == "ASSIGNED"


def test_full_lifecycle_updates_equipment_and_stock(api, pump, users, item):
    wo = create_wo(api, pump, users).data
    tech = api("TECHNICIAN")
    assert tech.post(f"/api/v1/work-orders/{wo['id']}/start/").status_code == 200
    pump.refresh_from_db()
    assert pump.status == "MAINTENANCE"

    r = tech.post(f"/api/v1/work-orders/{wo['id']}/parts/", {"item": item.pk, "quantity": "2"}, format="json")
    assert r.status_code == 201
    item.refresh_from_db()
    assert item.quantity == 8

    assert tech.post(f"/api/v1/work-orders/{wo['id']}/complete/", {}, format="json").status_code == 400  # notes required
    r = tech.post(f"/api/v1/work-orders/{wo['id']}/complete/",
                  {"completion_notes": "Seal replaced, leak test passed.", "labor_hours": "3.0", "downtime_hours": "4"}, format="json")
    assert r.status_code == 200 and r.data["status"] == "COMPLETED"
    assert Decimal(r.data["parts_cost"]) == 100 and Decimal(r.data["total_cost"]) == 100 + 3 * 35
    pump.refresh_from_db()
    assert pump.status == "OPERATIONAL" and pump.last_service_date is not None


def test_invalid_transitions(api, pump, users):
    wo = create_wo(api, pump, users).data
    r = api("TECHNICIAN").post(f"/api/v1/work-orders/{wo['id']}/complete/", {"completion_notes": "x"}, format="json")
    assert r.status_code == 400  # must be started first
    assert api("PLANT_MANAGER").post(f"/api/v1/work-orders/{wo['id']}/cancel/", {"reason": "dup"}, format="json").status_code == 200
    assert api("TECHNICIAN").post(f"/api/v1/work-orders/{wo['id']}/start/").status_code == 400


def test_unassigned_technician_blocked(api, pump, users):
    wo = create_wo(api, pump, users).data
    from apps.accounts.models import User
    other = User.objects.create_user("other@t.com", "Another-Pass-12!", first_name="Other", role="TECHNICIAN")
    from rest_framework.test import APIClient
    c = APIClient()
    c.force_authenticate(other)
    assert c.post(f"/api/v1/work-orders/{wo['id']}/start/").status_code == 403


def test_engineer_must_have_engineering_role(api, pump, users):
    r = create_wo(api, pump, users, engineer=users["VIEWER"].pk)
    assert r.status_code == 400


def test_filters_overdue_and_mine(api, pump, users):
    WorkOrder.objects.create(title="late", equipment=pump, deadline=timezone.now() - timedelta(days=1))
    create_wo(api, pump, users)
    c = api("TECHNICIAN")
    assert c.get("/api/v1/work-orders/?overdue=true").data["count"] == 1
    assert c.get("/api/v1/work-orders/?assigned_to_me=true").data["count"] == 1


def test_schedule_generates_work_order_once_and_completion_reschedules(api, pump, users):
    sch = MaintenanceSchedule.objects.create(equipment=pump, title="Quarterly", interval_days=90,
                                             next_due=timezone.localdate() + timedelta(days=2), assigned_engineer=users["ENGINEER"])
    assert generate_due_work_orders() == 1
    assert generate_due_work_orders() == 0  # idempotent
    wo = WorkOrder.objects.get(schedule=sch)
    assert wo.wo_type == "PREVENTIVE"
    api("ENGINEER").post(f"/api/v1/work-orders/{wo.pk}/start/")
    api("ENGINEER").post(f"/api/v1/work-orders/{wo.pk}/complete/", {"completion_notes": "Done"}, format="json")
    sch.refresh_from_db()
    pump.refresh_from_db()
    assert sch.next_due == timezone.localdate() + timedelta(days=90)
    assert pump.next_maintenance_date == sch.next_due
