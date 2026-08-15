from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_approved", "is_active")
    list_filter = ("role", "is_approved", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Profile", {"fields": ("role", "phone_number", "profile_photo", "is_email_verified", "is_approved")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "city", "is_default")
