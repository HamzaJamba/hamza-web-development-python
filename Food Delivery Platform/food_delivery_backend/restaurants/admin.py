from django.contrib import admin
from .models import Restaurant, WorkingHour


class WorkingHourInline(admin.TabularInline):
    model = WorkingHour
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "is_open", "avg_rating", "city")
    list_filter = ("status", "is_open", "city")
    search_fields = ("name", "owner__username")
    inlines = [WorkingHourInline]
