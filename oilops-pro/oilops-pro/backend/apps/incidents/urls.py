from rest_framework.routers import DefaultRouter

from .views import AttachmentViewSet, IncidentViewSet

router = DefaultRouter()
router.register("attachments", AttachmentViewSet, basename="incident-attachment")
router.register("", IncidentViewSet, basename="incident")
urlpatterns = router.urls
