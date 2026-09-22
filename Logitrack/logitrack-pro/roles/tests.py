from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Role, Permission

User = get_user_model()


class RolePermissionTests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.viewer_role = Role.objects.create(name=Role.VIEWER)

        self.admin_user = User.objects.create_user(
            email="admin@logitrack.com", password="StrongPass123", role=self.admin_role
        )
        self.viewer_user = User.objects.create_user(
            email="viewer@logitrack.com", password="StrongPass123", role=self.viewer_role
        )

    def test_admin_can_list_roles(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/roles/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_manage_roles(self):
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/roles/roles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_roles(self):
        response = self.client.get("/api/roles/roles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_has_permission_helper(self):
        perm = Permission.objects.create(codename="shipment.create")
        self.admin_role.permissions.add(perm)
        self.assertTrue(self.admin_role.has_permission("shipment.create"))
        self.assertFalse(self.viewer_role.has_permission("shipment.create"))

    def test_superuser_bypasses_role_check(self):
        superuser = User.objects.create_superuser(email="super@logitrack.com", password="StrongPass123")
        self.client.force_authenticate(user=superuser)
        response = self.client.get("/api/roles/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
