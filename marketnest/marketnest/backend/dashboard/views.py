from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from catalog.models import Product
from orders.models import Order, OrderItem
from roles.permissions import IsAdminRole
from vendors.models import Vendor
from vendors.permissions import IsApprovedVendor

User = get_user_model()


def f(v):
    return float(v or 0)


class VendorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsApprovedVendor]

    def get(self, request):
        vendor = request.user.vendor
        items = OrderItem.objects.filter(vendor=vendor).exclude(status=OrderItem.CANCELLED)
        totals = items.aggregate(revenue=Sum("line_total"), commission=Sum("commission"), sold=Sum("quantity"))
        revenue, commission = totals["revenue"] or Decimal("0"), totals["commission"] or Decimal("0")

        start = timezone.now().date() - timedelta(days=13)
        by_day = {
            r["day"]: r["rev"]
            for r in items.filter(order__created_at__date__gte=start)
            .annotate(day=TruncDate("order__created_at")).values("day").annotate(rev=Sum("line_total"))
        }
        daily = [{"date": (start + timedelta(days=i)).isoformat(),
                  "revenue": f(by_day.get(start + timedelta(days=i)))} for i in range(14)]

        products = Product.objects.filter(vendor=vendor)
        return Response({
            "revenue": f(revenue), "commission": f(commission), "net": f(revenue - commission),
            "commission_rate": f(vendor.commission_rate),
            "orders": items.values("order").distinct().count(), "items_sold": totals["sold"] or 0,
            "waiting": OrderItem.objects.filter(vendor=vendor, status=OrderItem.PENDING).count(),
            "low_stock": list(products.filter(is_active=True, stock__lte=5).order_by("stock").values("name", "slug", "stock")[:6]),
            "top_products": list(products.order_by("-sold_count").values("name", "slug", "sold_count")[:5]),
            "daily": daily,
        })


class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        items = OrderItem.objects.exclude(status=OrderItem.CANCELLED)
        agg = items.aggregate(gmv=Sum("line_total"), commission=Sum("commission"))
        top = (items.values("vendor__shop_name").annotate(revenue=Sum("line_total")).order_by("-revenue")[:5])
        return Response({
            "gmv": f(agg["gmv"]), "commission_earned": f(agg["commission"]),
            "orders": Order.objects.count(),
            "vendors": Vendor.objects.filter(is_approved=True).count(),
            "pending_vendors": Vendor.objects.filter(is_approved=False).count(),
            "customers": User.objects.filter(role__name="customer").count(),
            "top_vendors": [{"shop_name": r["vendor__shop_name"], "revenue": f(r["revenue"])} for r in top],
        })
