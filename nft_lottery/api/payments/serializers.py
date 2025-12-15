from rest_framework import serializers
from payments.models import Coupon, UserCoupon


class CouponSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Coupon
        fields = (
            "id",
            "name",
            "type",
            "type_display",
            "entries",
        )
        read_only_fields = fields


class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = UserCoupon
        fields = (
            "id",
            "coupon",
            "created_at",
        )
        read_only_fields = fields

