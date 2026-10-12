from rest_framework.routers import DefaultRouter
from .views import MachineViewSet

router = DefaultRouter()
router.register("", MachineViewSet, basename="machine")
urlpatterns = router.urls
