from decimal import Decimal

import pytest

from apps.notifications.models import Notification

pytestmark = pytest.mark.django_db


def test_stock_in_out_and_balance(api, item):
    c = api("STORE_KEEPER")
    r = c.post(f"/api/v1/inventory/{item.pk}/adjust/", {"movement_type": "IN", "quantity": "5"}, format="json")
    assert r.status_code == 201 and Decimal(r.data["balance_after"]) == 15
    r = c.post(f"/api/v1/inventory/{item.pk}/adjust/", {"movement_type": "OUT", "quantity": "3", "reference": "WO-1"}, format="json")
    assert Decimal(r.data["balance_after"]) == 12


def test_cannot_go_negative(api, item):
    r = api("STORE_KEEPER").post(f"/api/v1/inventory/{item.pk}/adjust/", {"movement_type": "OUT", "quantity": "99"}, format="json")
    assert r.status_code == 400
    item.refresh_from_db()
    assert item.quantity == 10


def test_low_stock_triggers_notification_once(api, users, item):
    c = api("STORE_KEEPER")
    c.post(f"/api/v1/inventory/{item.pk}/adjust/", {"movement_type": "OUT", "quantity": "7"}, format="json")  # 3 <= 4 reorder
    c.post(f"/api/v1/inventory/{item.pk}/adjust/", {"movement_type": "OUT", "quantity": "1"}, format="json")  # already low
    assert Notification.objects.filter(kind="LOW_STOCK", user=users["STORE_KEEPER"]).count() == 1
    assert len(c.get("/api/v1/inventory/low-stock/").data) == 1


def test_quantity_not_editable_directly(api, item):
    api("STORE_KEEPER").patch(f"/api/v1/inventory/{item.pk}/", {"quantity": "999", "name": "Renamed"}, format="json")
    item.refresh_from_db()
    assert item.quantity == 10 and item.name == "Renamed"


def test_opening_balance_creates_movement(api, plant):
    body = {"sku": "N-1", "name": "New", "category": "LUBRICANT", "unit": "L", "quantity": "40", "reorder_level": "10", "unit_cost": "3"}
    r = api("STORE_KEEPER").post("/api/v1/inventory/", body, format="json")
    assert r.status_code == 201 and Decimal(r.data["quantity"]) == 40
    assert api("STORE_KEEPER").get(f"/api/v1/inventory/movements/?item={r.data['id']}").data["count"] == 1
