from django.contrib import admin
from .models import ProductType, Product, PrizeType, Prize


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description")
    search_fields = ("name", "code")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "price_credits",
        "reward_tokens",
    )
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(PrizeType)
class PrizeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description")
    search_fields = ("name", "code")


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "rarity",
        "value_estimate",
    )
    list_filter = ("type", "rarity")
    search_fields = ("name",)
