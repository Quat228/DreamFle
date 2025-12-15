from users.models import User
from .models import UserCoupon, Coupon

def get_user_bonus_entries(user: User) -> int:
    return sum([user_coupon.coupon.entries for user_coupon in UserCoupon.objects.filter(user=user)])


def delete_user_coupons(user: User) -> int:
    deleted_count, _ = UserCoupon.objects.filter(user=user).delete()

    return deleted_count
