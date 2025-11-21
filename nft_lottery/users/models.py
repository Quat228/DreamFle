from django.contrib.auth.models import AbstractUser
from django.db import models

import uuid


def generate_ref_code():
    return uuid.uuid4().hex[:10]

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    referral_code = models.CharField(max_length=12, unique=True, default=generate_ref_code)

    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals"
    )

    token_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.username} ({self.telegram_id})"