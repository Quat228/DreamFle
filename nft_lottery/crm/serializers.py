from rest_framework import serializers
from lottery.models import Raffle


class CRMLoginSerializer(serializers.Serializer):
    """Serializer for CRM username/password login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UpdateRaffleStartTimeSerializer(serializers.Serializer):
    """Serializer for updating raffle start time."""
    new_start_at = serializers.DateTimeField(
        help_text="New start time for the raffle (timezone-aware datetime)"
    )
    
    def validate_new_start_at(self, value):
        """Validate that new start time is in the future."""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("New start time must be in the future")
        return value


class RaffleStartTimeUpdateResponseSerializer(serializers.Serializer):
    """Serializer for response after updating raffle start time."""
    raffle_id = serializers.IntegerField()
    raffle_name = serializers.CharField()
    old_start_at = serializers.DateTimeField()
    new_start_at = serializers.DateTimeField()
    task_rescheduled = serializers.BooleanField()
    task_info = serializers.DictField(required=False, allow_null=True)
    notify_task_info = serializers.DictField(required=False, allow_null=True)
    message = serializers.CharField()

