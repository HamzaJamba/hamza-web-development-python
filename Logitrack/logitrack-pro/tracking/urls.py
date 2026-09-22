from rest_framework.routers import DefaultRouter
from .views import GPSLogViewSet, IoTReadingViewSet

router = DefaultRouter()
router.register("gps", GPSLogViewSet, basename="gpslog")
router.register("iot", IoTReadingViewSet, basename="iotreading")

urlpatterns = router.urls
