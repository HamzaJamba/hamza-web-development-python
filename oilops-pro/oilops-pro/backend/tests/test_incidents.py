import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.notifications.models import Notification
from apps.workorders.models import WorkOrder

pytestmark = pytest.mark.django_db


def report(api, plant, role="TECHNICIAN", **extra):
    body = {"title": "Gas smell at manifold", "incident_type": "GAS_LEAK", "severity": "MAJOR", "plant": plant.pk,
            "description": "Detected H2S alarm", **extra}
    return api(role).post("/api/v1/incidents/", body, format="json")


def test_report_notifies_safety_and_manager(api, plant, users):
    r = report(api, plant)
    assert r.status_code == 201 and r.data["number"].startswith("INC-")
    assert Notification.objects.filter(kind="INCIDENT", user=users["SAFETY_OFFICER"], severity="critical").exists()
    assert Notification.objects.filter(kind="INCIDENT", user=users["PLANT_MANAGER"]).exists()


def test_equipment_failure_creates_work_order_and_marks_faulty(api, plant, pump):
    r = report(api, plant, incident_type="EQUIPMENT_FAILURE", equipment=pump.pk)
    assert r.status_code == 201
    pump.refresh_from_db()
    assert pump.status == "FAULTY"
    assert WorkOrder.objects.filter(equipment=pump, incident_id=r.data["id"]).exists()


def test_equipment_must_belong_to_plant(api, plant, pump):
    from apps.plants.models import Plant
    other = Plant.objects.create(name="Other", code="OTH")
    assert report(api, other, equipment=pump.pk).status_code == 400


def test_closing_requires_root_cause(api, plant):
    inc = report(api, plant).data
    c = api("SAFETY_OFFICER")
    assert c.patch(f"/api/v1/incidents/{inc['id']}/", {"status": "CLOSED"}, format="json").status_code == 400
    r = c.patch(f"/api/v1/incidents/{inc['id']}/", {"status": "CLOSED", "root_cause": "Seal wear", "corrective_action": "Replaced"}, format="json")
    assert r.status_code == 200 and r.data["closed_at"]


def test_attachment_upload_and_validation(api, plant, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    inc = report(api, plant).data
    c = api("SAFETY_OFFICER")
    url = f"/api/v1/incidents/{inc['id']}/attachments/"
    ok = c.post(url, {"file": SimpleUploadedFile("leak.png", b"\x89PNG\r\n", content_type="image/png")}, format="multipart")
    assert ok.status_code == 201 and ok.data["kind"] == "PHOTO"
    pdf = c.post(url, {"file": SimpleUploadedFile("report.pdf", b"%PDF-1.4")}, format="multipart")
    assert pdf.data["kind"] == "DOCUMENT"
    bad = c.post(url, {"file": SimpleUploadedFile("evil.exe", b"MZ")}, format="multipart")
    assert bad.status_code == 400
    settings.MAX_UPLOAD_MB = 0
    big = c.post(url, {"file": SimpleUploadedFile("big.txt", b"x" * 10)}, format="multipart")
    assert big.status_code == 400
    assert len(c.get(url).data) == 2
