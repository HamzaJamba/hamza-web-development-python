from django.contrib import admin

from .models import SparePartUsage, WorkOrder


class PartInline(admin.TabularInline):
    model = SparePartUsage
    extra = 0


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ["number", "title", "equipment", "wo_type", "priority", "status", "deadline"]
    list_filter = ["wo_type", "priority", "status"]
    inlines = [PartInline]
