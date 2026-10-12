from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(email="Test@FactoryPulse.io", password="StrongPass123")
        self.assertEqual(user.email, "Test@factorypulse.io")

    def test_create_superuser_flags(self):
        user = User.objects.create_superuser(email="root@factorypulse.io", password="StrongPass123")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
