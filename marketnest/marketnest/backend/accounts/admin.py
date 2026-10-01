from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "role", "is_active", "is_staff", "is_verified"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "is_staff", "is_active")}),
    )
    readonly_fields = ["date_joined", "last_login"]


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
