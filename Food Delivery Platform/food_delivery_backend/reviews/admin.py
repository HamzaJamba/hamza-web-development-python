from django.contrib import admin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "restaurant", "food_item", "rating", "is_flagged", "created_at")
    list_filter = ("rating", "is_flagged")
    inlines = [ReviewImageInline]
