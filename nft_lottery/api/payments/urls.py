from django.urls import path
from .views import UserCouponsAPIView, CouponDetailAPIView

urlpatterns = [
    path("coupons/", UserCouponsAPIView.as_view(), name="user-coupons"),
    path("coupons/<int:id>/", CouponDetailAPIView.as_view(), name="coupon-detail"),
]

