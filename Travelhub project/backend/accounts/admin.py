from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTP


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_approved', 'is_active')
    list_filter = ('role', 'is_verified', 'is_approved', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('TravelHub Info', {'fields': ('role', 'phone', 'profile_image', 'is_verified', 'is_approved')}),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'purpose', 'is_used', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used')
