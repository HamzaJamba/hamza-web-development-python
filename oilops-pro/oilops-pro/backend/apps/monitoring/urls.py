from rest_framework.routers import DefaultRouter

from .views import AlertViewSet, SensorReadingViewSet, ThresholdViewSet

router = DefaultRouter()
router.register("readings", SensorReadingViewSet, basename="reading")
router.register("alerts", AlertViewSet, basename="alert")
router.register("thresholds", ThresholdViewSet, basename="threshold")
urlpatterns = router.urls
