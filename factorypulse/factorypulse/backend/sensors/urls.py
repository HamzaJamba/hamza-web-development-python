from rest_framework.routers import DefaultRouter
from .views import SensorReadingViewSet

router = DefaultRouter()
router.register("readings", SensorReadingViewSet, basename="sensorreading")
urlpatterns = router.urls
