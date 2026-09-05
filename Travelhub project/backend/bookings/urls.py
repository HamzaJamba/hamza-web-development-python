from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, CouponViewSet

router = DefaultRouter()
router.register('coupons', CouponViewSet, basename='coupon')
router.register('', BookingViewSet, basename='booking')

urlpatterns = router.urls
