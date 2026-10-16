from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.employees.models import Department, Position
from apps.equipment.models import Equipment
from apps.inventory.models import Item
from apps.monitoring.models import Threshold
from apps.plants.models import Plant

PASSWORD = "Sup3r-Secret-Pass!"


def make_user(email, role, **kw):
    return User.objects.create_user(email=email, password=PASSWORD, first_name=email.split("@")[0], role=role, **kw)


@pytest.fixture
def users(db):
    return {r: make_user(f"{r.lower()}@t.com", r) for r in
            ["ADMIN", "PLANT_MANAGER", "ENGINEER", "TECHNICIAN", "SAFETY_OFFICER", "STORE_KEEPER", "HR", "VIEWER"]}


@pytest.fixture
def api(users):
    """api('ENGINEER') -> APIClient authenticated as that role."""
    def _client(role=None):
        c = APIClient()
        if role:
            c.force_authenticate(users[role])
        return c
    return _client


@pytest.fixture
def plant(db, users):
    return Plant.objects.create(name="Test Refinery", code="TR1", plant_type="REFINERY", manager=users["PLANT_MANAGER"],
                                latitude=24.8, longitude=67.0)


@pytest.fixture
def pump(plant):
    return Equipment.objects.create(plant=plant, name="Pump P-1", category="PUMP", serial_number="SN-1",
                                    purchase_date=date.today() - timedelta(days=400),
                                    warranty_expiry=date.today() + timedelta(days=100))


@pytest.fixture
def item(plant):
    return Item.objects.create(sku="SP-1", name="Seal kit", category="SPARE_PART", quantity=Decimal("10"),
                               reorder_level=Decimal("4"), unit_cost=Decimal("50"), plant=plant)


@pytest.fixture
def thresholds(db):
    Threshold.objects.create(metric="TEMPERATURE", max_value=95, severity="WARNING")
    Threshold.objects.create(metric="TEMPERATURE", max_value=110, severity="CRITICAL")


@pytest.fixture
def hr_structure(db):
    d = Department.objects.create(name="Maintenance", code="MNT")
    p = Position.objects.create(title="Technician", department=d)
    return d, p
