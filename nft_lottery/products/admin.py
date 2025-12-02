from django.contrib import admin
from django.utils.html import format_html
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
        "price",
        "entries_per_product",
    )
    list_filter = ("type",)
    search_fields = ("name",)
    readonly_fields = ("image_preview",)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Image Preview"
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'type', 'price', 'entries_per_product', 'metadata')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
    )


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
    readonly_fields = ("image_preview",)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Image Preview"
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'type', 'rarity', 'value_estimate', 'metadata')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
    )
