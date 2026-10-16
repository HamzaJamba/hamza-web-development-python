from rest_framework import serializers

from .models import Certification, Department, Employee, Position, SalaryGrade, Shift, TrainingRecord


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Department
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Position
        fields = "__all__"


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = "__all__"


class SalaryGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryGrade
        fields = "__all__"

    def validate(self, attrs):
        lo = attrs.get("min_salary", getattr(self.instance, "min_salary", None))
        hi = attrs.get("max_salary", getattr(self.instance, "max_salary", None))
        if lo is not None and hi is not None and lo > hi:
            raise serializers.ValidationError("min_salary cannot exceed max_salary.")
        return attrs


class TrainingRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = TrainingRecord
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Certification
        fields = "__all__"

    def validate(self, attrs):
        issued = attrs.get("issued_on", getattr(self.instance, "issued_on", None))
        exp = attrs.get("expires_on", getattr(self.instance, "expires_on", None))
        if issued and exp and exp < issued:
            raise serializers.ValidationError({"expires_on": "Expiry cannot be before issue date."})
        return attrs


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    position_title = serializers.CharField(source="position.title", read_only=True)
    shift_name = serializers.CharField(source="shift.name", read_only=True, default="")
    plant_name = serializers.CharField(source="plant.name", read_only=True, default="")
    grade_code = serializers.CharField(source="salary_grade.code", read_only=True, default="")

    class Meta:
        model = Employee
        fields = "__all__"

    def validate(self, attrs):
        dept = attrs.get("department", getattr(self.instance, "department", None))
        pos = attrs.get("position", getattr(self.instance, "position", None))
        if dept and pos and pos.department_id != dept.pk:
            raise serializers.ValidationError({"position": "Position does not belong to the selected department."})
        return attrs


class EmployeeDetailSerializer(EmployeeSerializer):
    trainings = TrainingRecordSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
