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
        "token_balance",
        "credit_balance",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "telegram_id", "referral_code")
    readonly_fields = ("referral_code",)
