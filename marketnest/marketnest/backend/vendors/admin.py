from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["shop_name", "owner", "city", "is_approved", "commission_rate"]
    list_filter = ["is_approved", "city"]
    search_fields = ["shop_name", "owner__email"]
