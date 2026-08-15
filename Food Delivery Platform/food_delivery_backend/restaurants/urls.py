from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import RestaurantViewSet, WorkingHourViewSet

router = DefaultRouter()
router.register("", RestaurantViewSet, basename="restaurant")

restaurants_router = nested_routers.NestedDefaultRouter(router, "", lookup="restaurant")
restaurants_router.register("hours", WorkingHourViewSet, basename="restaurant-hours")

urlpatterns = router.urls + restaurants_router.urls
