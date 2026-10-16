import pytest
from rest_framework.test import APIClient

from .conftest import PASSWORD

pytestmark = pytest.mark.django_db


def test_login_returns_tokens_and_user(users):
    r = APIClient().post("/api/v1/auth/login/", {"email": "engineer@t.com", "password": PASSWORD}, format="json")
    assert r.status_code == 200
    assert {"access", "refresh", "user"} <= set(r.data)
    assert r.data["user"]["role"] == "ENGINEER"


def test_login_wrong_password_is_logged_and_rejected(users):
    from apps.audit.models import AuditLog
    r = APIClient().post("/api/v1/auth/login/", {"email": "engineer@t.com", "password": "nope"}, format="json")
    assert r.status_code == 401
    assert AuditLog.objects.filter(action="LOGIN_FAILED").exists()


def test_refresh_and_logout_blacklists(users):
    c = APIClient()
    tokens = c.post("/api/v1/auth/login/", {"email": "viewer@t.com", "password": PASSWORD}, format="json").data
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    assert c.post("/api/v1/auth/logout/", {"refresh": tokens["refresh"]}, format="json").status_code == 204
    assert c.post("/api/v1/auth/refresh/", {"refresh": tokens["refresh"]}, format="json").status_code == 401


def test_requires_authentication(api):
    assert api().get("/api/v1/equipment/").status_code == 401


def test_me_cannot_escalate_role(api):
    c = api("VIEWER")
    r = c.patch("/api/v1/auth/me/", {"role": "ADMIN", "first_name": "Neo"}, format="json")
    assert r.status_code == 200
    assert r.data["role"] == "VIEWER" and r.data["first_name"] == "Neo"


def test_change_password_validates(api):
    c = api("VIEWER")
    assert c.post("/api/v1/auth/change-password/", {"old_password": "bad", "new_password": "Another-Long-Pass1!"}, format="json").status_code == 400
    assert c.post("/api/v1/auth/change-password/", {"old_password": PASSWORD, "new_password": "123"}, format="json").status_code == 400
    assert c.post("/api/v1/auth/change-password/", {"old_password": PASSWORD, "new_password": "Another-Long-Pass1!"}, format="json").status_code == 204


def test_user_admin_only(api):
    body = {"email": "new@t.com", "first_name": "New", "role": "TECHNICIAN", "password": "Valid-Pass-123!"}
    assert api("ENGINEER").post("/api/v1/auth/users/", body, format="json").status_code == 403
    r = api("ADMIN").post("/api/v1/auth/users/", body, format="json")
    assert r.status_code == 201 and "password" not in r.data


def test_directory_available_to_staff(api):
    r = api("ENGINEER").get("/api/v1/auth/users/directory/?role=TECHNICIAN")
    assert r.status_code == 200 and all(u["role"] == "TECHNICIAN" for u in r.data)
