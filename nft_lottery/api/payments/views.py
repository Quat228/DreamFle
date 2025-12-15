from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from payments.models import UserCoupon, Coupon
from .serializers import UserCouponSerializer, CouponSerializer


class UserCouponsAPIView(ListAPIView):
    """
    GET /api/payments/coupons/
    Returns list of coupons for the current user.
    """
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user).select_related('coupon').order_by('-created_at')


class CouponDetailAPIView(RetrieveAPIView):
    """
    GET /api/payments/coupons/<id>/
    Returns details of a specific coupon that the user owns.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        # Only return coupons that the user owns
        user_coupon_ids = UserCoupon.objects.filter(user=self.request.user).values_list('coupon_id', flat=True)
        return Coupon.objects.filter(id__in=user_coupon_ids)

