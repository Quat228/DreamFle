from django.contrib import admin
from .models import RaffleType, Raffle, Entry, Winner


@admin.register(RaffleType)
class RaffleTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description")
    search_fields = ("name", "code")


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0
    readonly_fields = ("user", "quantity", "created_at")


@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "prize",
        "is_active",
        "is_finished",
        "unlocked_at",
        "start_at",
        "end_at",
    )

    list_filter = ("type", "is_active", "is_finished")
    search_fields = ("name", "prize__name")
    inlines = [EntryInline]
    readonly_fields = (
        "created_at",
        "unlocked_at",
        "winner_selection_seed",
        "winner_selection_hash",
        "winner_selection_timestamp",
    )
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "type", "prize")
        }),
        ("Unlockable Settings", {
            "fields": ("min_entries_to_unlock", "draw_delay_days", "unlocked_at")
        }),
        ("Status", {
            "fields": ("is_active", "is_finished", "start_at", "end_at", "created_at")
        }),
        ("Winner Selection (Transparency)", {
            "fields": ("winner_selection_seed", "winner_selection_hash", "winner_selection_timestamp"),
            "classes": ("collapse",)
        }),
        ("Advanced", {
            "fields": ("logic_config",),
            "classes": ("collapse",)
        }),
    )


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ("raffle", "user", "entry", "created_at")
    search_fields = ("raffle__name", "user__username")
    readonly_fields = ("created_at",)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("user", "raffle", "quantity", "created_at")
    list_filter = ("raffle", "created_at")
    search_fields = ("user__username", "raffle__name")
    readonly_fields = ("created_at",)
