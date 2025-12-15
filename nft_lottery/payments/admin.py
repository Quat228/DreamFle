from django.contrib import admin
from .models import CreditTransaction, Coupon, UserCoupon


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "user__telegram_id")
    readonly_fields = ("created_at",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "entries")
    list_filter = ("type", "entries")
    search_fields = ("name", "type", "entries")


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ("user", "coupon", "created_at")
    list_filter = ("user", "coupon", "created_at")
    search_fields = ("user", "coupon")
    readonly_fields = ("created_at",)
