from django.contrib import admin

from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["serial_number", "name", "category", "plant", "status", "health_score"]
    list_filter = ["category", "status", "plant"]
    search_fields = ["serial_number", "name"]
