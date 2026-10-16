from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("departments", views.DepartmentViewSet, basename="department")
router.register("positions", views.PositionViewSet, basename="position")
router.register("shifts", views.ShiftViewSet, basename="shift")
router.register("salary-grades", views.SalaryGradeViewSet, basename="salarygrade")
router.register("trainings", views.TrainingRecordViewSet, basename="training")
router.register("certifications", views.CertificationViewSet, basename="certification")
router.register("", views.EmployeeViewSet, basename="employee")
urlpatterns = router.urls
