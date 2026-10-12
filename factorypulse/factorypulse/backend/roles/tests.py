from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Role

User = get_user_model()


class RolePermissionTests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.operator_role = Role.objects.create(name=Role.OPERATOR)
        self.admin = User.objects.create_user(email="admin2@factorypulse.io", password="StrongPass123", role=self.admin_role)

    def test_admin_can_list_roles(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_blocked(self):
        response = self.client.get("/api/roles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
