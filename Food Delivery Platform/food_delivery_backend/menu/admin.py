from django.contrib import admin
from .models import Category, FoodItem, FoodImage, WishlistItem


class FoodImageInline(admin.TabularInline):
    model = FoodImage
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "price", "is_available", "avg_rating")
    list_filter = ("is_available", "category")
    search_fields = ("name", "restaurant__name")
    inlines = [FoodImageInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("customer", "food_item", "added_at")
