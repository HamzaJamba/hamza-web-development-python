from datetime import date, timedelta

import pytest
from django.test import override_settings

from apps.employees.models import Certification, Employee
from apps.employees.tasks import check_certification_expiry
from apps.notifications.models import Notification
from apps.notifications.services import notify

pytestmark = pytest.mark.django_db


def test_health_endpoint(api):
    r = api().get("/api/health/")
    assert r.status_code == 200 and r.data["database"] == "ok"


def test_swagger_and_schema_available(api):
    assert api().get("/api/schema/").status_code == 200
    assert api().get("/api/docs/").status_code == 200
    assert api().get("/api/redoc/").status_code == 200


def test_notifications_are_private_and_markable(api, users):
    notify([users["ENGINEER"]], "SYSTEM", "Hello", "world")
    notify([users["VIEWER"]], "SYSTEM", "Secret", "x")
    c = api("ENGINEER")
    assert c.get("/api/v1/notifications/").data["count"] == 1
    assert c.get("/api/v1/notifications/unread-count/").data["count"] == 1
    nid = c.get("/api/v1/notifications/").data["results"][0]["id"]
    assert c.post(f"/api/v1/notifications/{nid}/read/").data["is_read"] is True
    assert c.get("/api/v1/notifications/unread-count/").data["count"] == 0
    other = Notification.objects.get(user=users["VIEWER"])
    assert c.post(f"/api/v1/notifications/{other.pk}/read/").status_code == 404


def test_email_sent_for_emailed_notification(users, mailoutbox):
    notify([users["ENGINEER"]], "ALERT", "Boom", "details", email=True)
    assert len(mailoutbox) == 1 and "[OilOps] Boom" in mailoutbox[0].subject


def test_certification_expiry_task(users, hr_structure):
    d, p = hr_structure
    e = Employee.objects.create(employee_id="E1", first_name="A", last_name="B", department=d, position=p)
    Certification.objects.create(employee=e, name="Rigging", issued_on=date.today() - timedelta(days=300),
                                 expires_on=date.today() + timedelta(days=10))
    assert check_certification_expiry() == 1
    assert check_certification_expiry() == 0  # de-duplicated
    assert Notification.objects.filter(kind="CERTIFICATION", user=users["HR"]).exists()


def test_employee_position_must_match_department(api, hr_structure):
    from apps.employees.models import Department
    d, p = hr_structure
    other = Department.objects.create(name="Ops", code="OPS")
    body = {"employee_id": "E9", "first_name": "A", "last_name": "B", "department": other.pk, "position": p.pk}
    assert api("HR").post("/api/v1/employees/", body, format="json").status_code == 400


def test_tank_level_cannot_exceed_capacity(api, plant):
    body = {"plant": plant.pk, "tag": "T1", "product": "DIESEL", "capacity_litres": "1000", "current_level_litres": "2000"}
    assert api("ENGINEER").post("/api/v1/plants/tanks/", body, format="json").status_code == 400


def test_pipeline_endpoints_differ(api, plant):
    body = {"name": "L", "code": "P1", "origin": plant.pk, "destination": plant.pk}
    assert api("ENGINEER").post("/api/v1/plants/pipelines/", body, format="json").status_code == 400


def test_error_payload_shape(api):
    r = api("HR").post("/api/v1/employees/", {}, format="json")
    assert r.status_code == 400 and "errors" in r.data and r.data["detail"]


@override_settings(REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("apps.core.permissions.RoleBasedPermission",),
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.AnonRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {"anon": "2/min"},
})
def test_rate_limiting_class_is_active(api):
    from django.core.cache import cache
    from rest_framework.settings import api_settings
    cache.clear()
    api_settings.reload()
    try:
        from rest_framework.test import APIClient
        from apps.accounts.views import LoginView
        LoginView.throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
        codes = [APIClient().post("/api/v1/auth/login/", {"email": "a@b.c", "password": "x"}, format="json").status_code for _ in range(4)]
        assert 429 in codes
    finally:
        LoginView.throttle_classes = []
