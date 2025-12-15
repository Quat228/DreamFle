from django.db import models

from users.models import User
from products.models import Product


class CreditTransaction(models.Model):
    TYPES = (
        ("purchase", "Credit purchase"),
        ("bonus", "Credit bonus"),
        ("spend", "Spend"),
        ("admin", "Admin adjustment"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.type} {self.amount}"


class Coupon(models.Model):
    TYPES = (
        ("referral", "Coupon referral"),
        ("lost", "Coupon lost"),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPES)
    entries = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.type} {self.entries}"


class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.coupon} - {self.created_at}"


class ProductPurchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_purchases")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_purchases")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} - {self.amount}"
