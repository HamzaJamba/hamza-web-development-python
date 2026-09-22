from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Shipment

User = get_user_model()


class ShipmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="ops@logitrack.com", password="StrongPass123")
        self.client.force_authenticate(user=self.user)

    def test_create_shipment_generates_tracking_number(self):
        payload = {
            "customer_name": "Acme Corp",
            "origin": "Lahore",
            "destination": "Karachi",
            "weight_kg": "150.00",
        }
        response = self.client.post("/api/shipments/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["tracking_number"].startswith("LTP"))

    def test_update_status_creates_history(self):
        shipment = Shipment.objects.create(
            customer_name="Acme Corp", origin="Lahore", destination="Karachi",
            weight_kg=100, created_by=self.user,
        )
        response = self.client.post(
            f"/api/shipments/{shipment.id}/update-status/",
            {"status": "in_transit", "note": "Left warehouse"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, "in_transit")
        self.assertEqual(shipment.status_history.count(), 1)

    def test_list_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/shipments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
