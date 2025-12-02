from django.db import models
from django.conf import settings


class CreditTransaction(models.Model):
    TYPES = (
        ("purchase", "Credit purchase"),
        ("bonus", "Credit bonus"),
        ("spend", "Spend"),
        ("admin", "Admin adjustment"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.type} {self.amount}"