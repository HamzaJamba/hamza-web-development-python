from django.db.models import Count
from rest_framework import viewsets

from apps.accounts.models import Role
from apps.audit.mixins import AuditMixin

from . import serializers as s
from .models import Certification, Department, Employee, Position, SalaryGrade, Shift, TrainingRecord

HR_ROLES = [Role.HR, Role.PLANT_MANAGER]


class DepartmentViewSet(AuditMixin, viewsets.ModelViewSet):
    serializer_class = s.DepartmentSerializer
    write_roles = HR_ROLES
    search_fields = ["name", "code"]

    def get_queryset(self):
        return Department.objects.annotate(employee_count=Count("employees"))


class PositionViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Position.objects.select_related("department")
    serializer_class = s.PositionSerializer
    write_roles = HR_ROLES
    filterset_fields = ["department"]
    search_fields = ["title"]


class ShiftViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = s.ShiftSerializer
    write_roles = HR_ROLES


class SalaryGradeViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = SalaryGrade.objects.all()
    serializer_class = s.SalaryGradeSerializer
    read_roles = HR_ROLES  # salary information is confidential
    write_roles = [Role.HR]


class EmployeeViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department", "position", "shift", "salary_grade", "plant")
    write_roles = HR_ROLES
    filterset_fields = ["department", "position", "shift", "plant", "status"]
    search_fields = ["first_name", "last_name", "employee_id", "email"]
    ordering_fields = ["first_name", "hire_date", "employee_id"]

    def get_serializer_class(self):
        return s.EmployeeDetailSerializer if self.action == "retrieve" else s.EmployeeSerializer


class TrainingRecordViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = TrainingRecord.objects.select_related("employee")
    serializer_class = s.TrainingRecordSerializer
    write_roles = HR_ROLES + [Role.SAFETY_OFFICER]
    filterset_fields = ["employee"]
    search_fields = ["title", "provider"]


class CertificationViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = Certification.objects.select_related("employee")
    serializer_class = s.CertificationSerializer
    write_roles = HR_ROLES + [Role.SAFETY_OFFICER]
    filterset_fields = ["employee"]
    search_fields = ["name", "issuer", "certificate_no"]
    ordering_fields = ["expires_on", "issued_on"]
