from django.db import models

from products.models import Prize


RAFFLE_TYPES = (
        ("simple", "Simple Raffle"),
        ("unlockable", "Unlockable after min participants"),
        ("time", "Time-limited"),
        ("progressive", "Progressive prize"),
    )


class RaffleType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def str(self):
        return f"{self.name} ({self.code})"


class Raffle(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type = models.ForeignKey(RaffleType, on_delete=models.CASCADE)
    prize = models.OneToOneField(Prize, on_delete=models.PROTECT, related_name="raffle")
    cost_tokens = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_participants_to_unlock = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_finished = models.BooleanField(default=False)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logic_config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.type.name})"


class Entry(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="entries")
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name="entries")
    created_at = models.DateTimeField(auto_now_add=True)
    cost_tokens = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} → {self.raffle}"


class Winner(models.Model):
    raffle = models.OneToOneField(Raffle, on_delete=models.CASCADE, related_name="winner")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} won {self.raffle}"
