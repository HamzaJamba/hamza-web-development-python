from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You do not have permission to access this page.")


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["ADMIN"]


class AdminOrReceptionistRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["ADMIN", "RECEPTIONIST"]


class DoctorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["ADMIN", "DOCTOR"]


class StaffRequiredMixin(RoleRequiredMixin):
    """Any logged-in staff member: Admin, Doctor, or Receptionist."""
    allowed_roles = ["ADMIN", "DOCTOR", "RECEPTIONIST"]
