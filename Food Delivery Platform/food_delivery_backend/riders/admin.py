from django.contrib import admin
from .models import Rider, Delivery


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ("user", "is_online", "total_deliveries", "total_earnings")


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("order", "rider", "status", "assigned_at", "delivered_at")
    list_filter = ("status",)
