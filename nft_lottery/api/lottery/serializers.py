from datetime import timedelta
from rest_framework import serializers
from lottery.models import Raffle, Entry, RaffleType
from products.models import Prize


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prize
        fields = (
            "id",
            "name",
            "description",
            "image",
            "rarity",
            "value_estimate",
        )
        read_only_fields = fields


class RaffleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RaffleType
        fields = ("id", "name", "code", "description")
        read_only_fields = fields


class RaffleSerializer(serializers.ModelSerializer):
    prize = PrizeSerializer(read_only=True)
    type = RaffleTypeSerializer(read_only=True)
    entries_count = serializers.SerializerMethodField()
    winner = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    draw_date = serializers.SerializerMethodField()
    transparency_data = serializers.SerializerMethodField()

    class Meta:
        model = Raffle
        fields = (
            "id",
            "name",
            "description",
            "type",
            "prize",
            "cost_tokens",
            "min_participants_to_unlock",
            "is_active",
            "is_finished",
            "start_at",
            "end_at",
            "created_at",
            "entries_count",
            "winner",
            "unlocked_at",
            "draw_delay_days",
            "is_unlocked",
            "draw_date",
            "transparency_data",
        )
        read_only_fields = fields

    def get_entries_count(self, obj):
        return obj.entries.count()

    def get_winner(self, obj):
        if obj.is_finished:
            try:
                # Check if winner relationship exists
                if hasattr(obj, 'winner') and obj.winner is not None:
                    return {
                        "id": obj.winner.user.id,
                        "username": obj.winner.user.username,
                    }
            except Exception:
                # Winner doesn't exist or relationship is broken
                pass
        return None

    def get_is_unlocked(self, obj):
        """Check if raffle is unlocked (unlocked_at is set)."""
        return obj.unlocked_at is not None

    def get_draw_date(self, obj):
        """Get the draw date (start_at if set, or calculated from unlocked_at + delay)."""
        if obj.start_at:
            return obj.start_at
        if obj.unlocked_at and obj.draw_delay_days:
            return obj.unlocked_at + timedelta(days=obj.draw_delay_days)
        return None

    def get_transparency_data(self, obj):
        """Get transparency data for finished raffles."""
        if not obj.is_finished:
            return None
        
        transparency = {
            "selection_method": "SHA256 hash-based selection",
        }
        
        if obj.winner_selection_seed:
            transparency["selection_seed"] = obj.winner_selection_seed
        if obj.winner_selection_hash:
            transparency["selection_hash"] = obj.winner_selection_hash
        if obj.winner_selection_timestamp:
            transparency["selection_timestamp"] = obj.winner_selection_timestamp.isoformat()
        
        return transparency if transparency.get("selection_seed") else None


class EntrySerializer(serializers.ModelSerializer):
    raffle = RaffleSerializer(read_only=True)

    class Meta:
        model = Entry
        fields = (
            "id",
            "raffle",
            "cost_tokens",
            "created_at",
        )
        read_only_fields = fields



