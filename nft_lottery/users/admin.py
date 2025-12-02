from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "telegram_id",
        "referral_code",
        "referred_by",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "telegram_id", "referral_code")
    readonly_fields = ("referral_code", "telegram_id")

    fieldsets = (
        ("Info", {
            "fields": ("username", "password")
        }),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "telegram_id",
                "referral_code",
                "referred_by",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )
