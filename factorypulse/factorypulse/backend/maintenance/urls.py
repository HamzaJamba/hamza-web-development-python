from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, PredictiveMaintenanceView

router = DefaultRouter()
router.register("work-orders", WorkOrderViewSet, basename="workorder")
router.register("predict", PredictiveMaintenanceView, basename="predict")
urlpatterns = router.urls
