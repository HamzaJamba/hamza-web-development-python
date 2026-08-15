from datetime import timedelta

from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdmin, IsRestaurantOwner
from menu.models import FoodItem
from orders.models import Order
from restaurants.models import Restaurant
from .models import PlatformSettings
from .serializers import PlatformSettingsSerializer


COMPLETED = Order.Status.COMPLETED


def _daily_sales(qs, days=30):
    since = timezone.now() - timedelta(days=days)
    rows = (
        qs.filter(status=COMPLETED, placed_at__gte=since)
        .annotate(day=TruncDate("placed_at"))
        .values("day")
        .annotate(revenue=Sum("grand_total"), orders=Count("id"))
        .order_by("day")
    )
    return list(rows)


class AdminDashboardView(APIView):
    """
    GET /api/dashboard/admin/  — platform-wide stats for the Admin dashboard.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        completed_orders = Order.objects.filter(status=COMPLETED)

        totals = {
            "total_restaurants": Restaurant.objects.count(),
            "approved_restaurants": Restaurant.objects.filter(status=Restaurant.Status.APPROVED).count(),
            "pending_restaurants": Restaurant.objects.filter(status=Restaurant.Status.PENDING).count(),
            "total_riders": User.objects.filter(role=User.Role.RIDER).count(),
            "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
            "active_customers_30d": Order.objects.filter(placed_at__gte=month_start)
                .values("customer").distinct().count(),
            "total_orders": Order.objects.count(),
            "total_revenue": completed_orders.aggregate(v=Sum("grand_total"))["v"] or 0,
            "total_commission_earned": completed_orders.aggregate(v=Sum("platform_commission_amount"))["v"] or 0,
            "total_restaurant_payouts": completed_orders.aggregate(v=Sum("restaurant_payout"))["v"] or 0,
        }

        sales = {
            "today_revenue": completed_orders.filter(placed_at__gte=today_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "week_revenue": completed_orders.filter(placed_at__gte=week_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "month_revenue": completed_orders.filter(placed_at__gte=month_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "daily_series_30d": _daily_sales(Order.objects, days=30),
        }

        popular_foods = list(
            FoodItem.objects.order_by("-total_orders")[:10]
            .values("id", "name", "restaurant__name", "total_orders", "avg_rating")
        )

        order_status_breakdown = list(
            Order.objects.values("status").annotate(count=Count("id")).order_by("-count")
        )

        return Response({
            "totals": totals,
            "sales": sales,
            "popular_foods": popular_foods,
            "order_status_breakdown": order_status_breakdown,
        })


class RestaurantDashboardView(APIView):
    """
    GET /api/dashboard/restaurant/?restaurant_id=<uuid>  — stats for one of the owner's restaurants.
    If the owner has only one restaurant, restaurant_id may be omitted.
    """

    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwner]

    def get(self, request):
        restaurant_id = request.query_params.get("restaurant_id")
        qs = Restaurant.objects.filter(owner=request.user)
        if restaurant_id:
            restaurant = qs.filter(id=restaurant_id).first()
        else:
            restaurant = qs.first()

        if not restaurant:
            return Response({"detail": "No restaurant found for this owner."}, status=404)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        orders = Order.objects.filter(restaurant=restaurant)
        completed = orders.filter(status=COMPLETED)

        sales = {
            "today_revenue": completed.filter(placed_at__gte=today_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "today_orders": orders.filter(placed_at__gte=today_start).count(),
            "week_revenue": completed.filter(placed_at__gte=week_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "month_revenue": completed.filter(placed_at__gte=month_start).aggregate(v=Sum("grand_total"))["v"] or 0,
            "daily_series_30d": _daily_sales(orders, days=30),
        }

        payouts = {
            "total_payout_all_time": completed.aggregate(v=Sum("restaurant_payout"))["v"] or 0,
            "total_commission_paid_all_time": completed.aggregate(v=Sum("platform_commission_amount"))["v"] or 0,
            "month_payout": completed.filter(placed_at__gte=month_start).aggregate(v=Sum("restaurant_payout"))["v"] or 0,
        }

        best_selling = list(
            FoodItem.objects.filter(restaurant=restaurant).order_by("-total_orders")[:10]
            .values("id", "name", "total_orders", "avg_rating", "price")
        )

        order_status_breakdown = list(
            orders.values("status").annotate(count=Count("id")).order_by("-count")
        )

        return Response({
            "restaurant": {"id": restaurant.id, "name": restaurant.name, "avg_rating": restaurant.avg_rating},
            "sales": sales,
            "payouts": payouts,
            "best_selling_food": best_selling,
            "order_status_breakdown": order_status_breakdown,
            "total_orders_all_time": orders.count(),
        })


class PlatformSettingsView(APIView):
    """GET/PATCH /api/dashboard/settings/ — admin-only platform configuration (delivery fee, tax, commission...)."""

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response(PlatformSettingsSerializer(PlatformSettings.load()).data)

    def patch(self, request):
        settings_obj = PlatformSettings.load()
        serializer = PlatformSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
