from rest_framework import serializers
from users.models import User
from payments.services import get_user_bonus_entries


class UserMeSerializer(serializers.ModelSerializer):
    bonus_entries = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "telegram_id",
            "referral_code",
            "referred_by",
            "date_joined",
            "bonus_entries",
        )
        read_only_fields = fields

    def get_bonus_entries(self, obj):
        """Calculate total bonus entries from user's coupons."""
        return get_user_bonus_entries(user=obj)


class ReferralUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "telegram_id", "date_joined")
