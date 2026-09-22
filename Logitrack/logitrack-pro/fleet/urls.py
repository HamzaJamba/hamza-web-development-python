from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, MaintenanceRecordViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("maintenance", MaintenanceRecordViewSet, basename="maintenance")

urlpatterns = router.urls
