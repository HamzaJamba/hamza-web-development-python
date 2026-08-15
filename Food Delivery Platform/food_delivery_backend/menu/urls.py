from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import CategoryViewSet, FoodItemViewSet, FoodImageViewSet, WishlistViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("food-items", FoodItemViewSet, basename="food-item")
router.register("wishlist", WishlistViewSet, basename="wishlist")

food_items_router = nested_routers.NestedDefaultRouter(router, "food-items", lookup="food_item")
food_items_router.register("images", FoodImageViewSet, basename="food-item-images")

urlpatterns = router.urls + food_items_router.urls
