from rest_framework.routers import DefaultRouter

from .views import MaintenanceScheduleViewSet

router = DefaultRouter()
router.register("schedules", MaintenanceScheduleViewSet, basename="schedule")
urlpatterns = router.urls
