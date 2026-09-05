from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, RoomAvailabilityViewSet

router = DefaultRouter()
router.register('availability', RoomAvailabilityViewSet, basename='room-availability')
router.register('', RoomViewSet, basename='room')

urlpatterns = router.urls
