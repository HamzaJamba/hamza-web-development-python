import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.monitoring.models import Alert, Threshold
from apps.notifications.models import Notification
from apps.workorders.models import WorkOrder

pytestmark = pytest.mark.django_db
URL = "/api/v1/monitoring/readings/"


def post(c, eq, value, metric="TEMPERATURE"):
    return c.post(URL, {"equipment": eq.pk, "metric": metric, "value": value}, format="json")


def test_normal_reading_no_alert(api, pump, thresholds):
    assert post(api("TECHNICIAN"), pump, 70).status_code == 201
    assert Alert.objects.count() == 0 and pump.health_score == 100


def test_warning_then_escalation_then_autoresolve(api, pump, thresholds, users):
    c = api("TECHNICIAN")
    post(c, pump, 100)
    a = Alert.objects.get()
    assert a.severity == "WARNING" and a.occurrence_count == 1
    post(c, pump, 102)
    a.refresh_from_db()
    assert a.occurrence_count == 2 and Alert.objects.count() == 1  # de-duplicated
    post(c, pump, 120)
    a.refresh_from_db()
    assert a.severity == "CRITICAL"
    pump.refresh_from_db()
    assert pump.health_score == 75
    post(c, pump, 60)
    a.refresh_from_db()
    assert a.status == "RESOLVED"
    pump.refresh_from_db()
    assert pump.health_score == 100


def test_critical_alert_notifies_and_creates_emergency_wo_once(api, pump, thresholds, users):
    c = api("TECHNICIAN")
    post(c, pump, 130)
    post(c, pump, 135)
    assert Notification.objects.filter(kind="ALERT", user=users["ENGINEER"], severity="critical").count() == 1
    assert WorkOrder.objects.filter(equipment=pump, wo_type="EMERGENCY").count() == 1


@override_settings(AUTO_WORK_ORDER_ON_CRITICAL_ALERT=False)
def test_auto_work_order_can_be_disabled(api, pump, thresholds):
    post(api("TECHNICIAN"), pump, 130)
    assert WorkOrder.objects.count() == 0


def test_equipment_threshold_overrides_category(api, pump, thresholds):
    Threshold.objects.create(equipment=pump, metric="TEMPERATURE", max_value=60, severity="WARNING")
    post(api("TECHNICIAN"), pump, 70)
    assert Alert.objects.filter(severity="WARNING").count() == 1


def test_bulk_ingest(api, pump, thresholds):
    data = [{"equipment": pump.pk, "metric": "TEMPERATURE", "value": v} for v in (70, 72, 74)]
    r = api("TECHNICIAN").post(URL, data, format="json")
    assert r.status_code == 201 and r.data["accepted"] == 3


@override_settings(IOT_DEVICE_API_KEY="k3y")
def test_device_key_auth(pump, thresholds):
    c = APIClient()
    assert post(c, pump, 70).status_code == 401
    c.credentials(HTTP_X_DEVICE_KEY="wrong")
    assert post(c, pump, 70).status_code == 401
    c.credentials(HTTP_X_DEVICE_KEY="k3y")
    assert post(c, pump, 70).status_code == 201
    assert c.get("/api/v1/equipment/").status_code == 401  # the key only opens telemetry ingest


def test_viewer_cannot_ingest(api, pump):
    assert post(api("VIEWER"), pump, 70).status_code == 403


def test_threshold_validation(api, pump):
    c = api("ENGINEER")
    assert c.post("/api/v1/monitoring/thresholds/", {"metric": "PRESSURE", "severity": "WARNING"}, format="json").status_code == 400
    assert c.post("/api/v1/monitoring/thresholds/", {"metric": "PRESSURE", "min_value": 9, "max_value": 1, "severity": "WARNING"}, format="json").status_code == 400


def test_latest_and_series(api, pump, thresholds):
    post(api("TECHNICIAN"), pump, 101)
    r = api("VIEWER").get(f"{URL}latest/?equipment={pump.pk}")
    assert r.data[0]["metric"] == "TEMPERATURE" and r.data[0]["state"] == "WARNING"
    assert len(api("VIEWER").get(f"{URL}series/?equipment={pump.pk}&metric=TEMPERATURE").data) == 1


def test_acknowledge_and_resolve_alert(api, pump, thresholds):
    post(api("TECHNICIAN"), pump, 101)
    a = Alert.objects.get()
    assert api("VIEWER").post(f"/api/v1/monitoring/alerts/{a.pk}/acknowledge/").status_code == 403
    assert api("TECHNICIAN").post(f"/api/v1/monitoring/alerts/{a.pk}/acknowledge/").data["status"] == "ACKNOWLEDGED"
    assert api("TECHNICIAN").post(f"/api/v1/monitoring/alerts/{a.pk}/resolve/").data["status"] == "RESOLVED"
