from rest_framework import serializers
from users.models import User


class UserMeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "telegram_id",
            "referral_code",
            "referred_by",
            "date_joined",
        )
        read_only_fields = fields


class ReferralUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "telegram_id", "date_joined")
