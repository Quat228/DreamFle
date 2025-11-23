from django.contrib import admin
from .models import TokenTransaction, CreditTransaction


@admin.register(TokenTransaction)
class TokenTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "user__telegram_id")
    readonly_fields = ("created_at",)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "user__telegram_id")
    readonly_fields = ("created_at",)
