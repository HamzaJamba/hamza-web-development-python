import pytest

pytestmark = pytest.mark.django_db

EQUIP_BODY = lambda plant: {"plant": plant.pk, "name": "New pump", "category": "PUMP", "serial_number": "SN-NEW"}  # noqa: E731


@pytest.mark.parametrize("role,expected", [
    ("ADMIN", 201), ("PLANT_MANAGER", 201), ("ENGINEER", 201), ("TECHNICIAN", 403), ("SAFETY_OFFICER", 403),
    ("STORE_KEEPER", 403), ("HR", 403), ("VIEWER", 403)])
def test_equipment_write_matrix(api, plant, role, expected):
    assert api(role).post("/api/v1/equipment/", EQUIP_BODY(plant), format="json").status_code == expected


@pytest.mark.parametrize("role", ["ADMIN", "TECHNICIAN", "VIEWER", "HR"])
def test_everyone_authenticated_can_read_equipment(api, pump, role):
    assert api(role).get("/api/v1/equipment/").status_code == 200


@pytest.mark.parametrize("role,expected", [("HR", 200), ("PLANT_MANAGER", 200), ("TECHNICIAN", 403), ("VIEWER", 403)])
def test_salary_grades_are_confidential(api, role, expected):
    assert api(role).get("/api/v1/employees/salary-grades/").status_code == expected


@pytest.mark.parametrize("role,expected", [("STORE_KEEPER", 201), ("PLANT_MANAGER", 201), ("TECHNICIAN", 403), ("VIEWER", 403)])
def test_inventory_write_matrix(api, plant, role, expected):
    body = {"sku": "X-1", "name": "Thing", "category": "CHEMICAL", "unit": "L", "reorder_level": "5", "unit_cost": "2"}
    assert api(role).post("/api/v1/inventory/", body, format="json").status_code == expected


@pytest.mark.parametrize("role,expected", [("ADMIN", 200), ("PLANT_MANAGER", 403), ("ENGINEER", 403)])
def test_audit_logs_admin_only(api, role, expected):
    assert api(role).get("/api/v1/audit/logs/").status_code == expected


@pytest.mark.parametrize("role,expected", [("PLANT_MANAGER", 200), ("SAFETY_OFFICER", 200), ("TECHNICIAN", 403), ("VIEWER", 403)])
def test_reports_roles(api, role, expected):
    assert api(role).get("/api/v1/reports/maintenance/").status_code == expected


def test_viewer_cannot_report_incident(api, plant):
    body = {"title": "x", "incident_type": "NEAR_MISS", "plant": plant.pk, "description": "d"}
    assert api("VIEWER").post("/api/v1/incidents/", body, format="json").status_code == 403
    assert api("TECHNICIAN").post("/api/v1/incidents/", body, format="json").status_code == 201
