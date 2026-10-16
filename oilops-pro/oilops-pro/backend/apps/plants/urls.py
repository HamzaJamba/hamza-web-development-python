from rest_framework.routers import DefaultRouter

from .views import PipelineViewSet, PlantViewSet, StorageTankViewSet

router = DefaultRouter()
router.register("pipelines", PipelineViewSet, basename="pipeline")
router.register("tanks", StorageTankViewSet, basename="tank")
router.register("", PlantViewSet, basename="plant")
urlpatterns = router.urls
