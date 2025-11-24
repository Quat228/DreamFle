from rest_framework import serializers


class TelegramAuthRequestSerializer(serializers.Serializer):
    init_data_raw = serializers.CharField(required=True)
