from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class VehicleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="fleet@logitrack.com", password="StrongPass123")
        self.client.force_authenticate(user=self.user)

    def test_create_vehicle(self):
        payload = {"vehicle_number": "TRK-500", "capacity_kg": "3000", "truck_type": "truck"}
        response = self.client.post("/api/fleet/vehicles/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_vehicle_number_rejected(self):
        payload = {"vehicle_number": "TRK-500", "capacity_kg": "3000"}
        self.client.post("/api/fleet/vehicles/", payload, format="json")
        response = self.client.post("/api/fleet/vehicles/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
