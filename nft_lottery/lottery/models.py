import secrets
from django.db import models

from products.models import Prize


RAFFLE_TYPES = (
        ("simple", "Simple Raffle"),
        ("unlockable", "Unlockable after min participants"),
        ("time", "Time-limited"),
        ("progressive", "Progressive prize"),
    )

RAFFLE_STATUSES = (
    ("OPEN", "Open"),
    ("COUNTDOWN", "Countdown"),
    ("FINISHING", "Finishing"),
    ("FINISHED", "Finished"),
)

def generate_seed():
    return secrets.token_hex(32)


class RaffleType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    
class Raffle(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type = models.ForeignKey(RaffleType, on_delete=models.CASCADE)
    prize = models.OneToOneField(Prize, on_delete=models.PROTECT, related_name="raffle")
    min_entries_to_unlock = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_finished = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=RAFFLE_STATUSES, default="OPEN")
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logic_config = models.JSONField(null=True, blank=True)
    unlocked_at = models.DateTimeField(null=True, blank=True, help_text="When min_entries was reached")
    draw_delay_days = models.PositiveIntegerField(default=3, help_text="Days to wait after unlock before draw")
    winner_selection_seed = models.CharField(max_length=64, null=True, blank=True,
                                             help_text="Public seed for transparent selection")
    winner_selection_hash = models.CharField(max_length=64, null=True, blank=True,
                                             help_text="Hash used for winner selection")
    winner_selection_timestamp = models.DateTimeField(null=True, blank=True, help_text="When winner was selected")

    def __str__(self):
        return f"{self.name} ({self.type.name})"

    def save(self, *args, **kwargs):
        # Generate seed when creating a new raffle (for transparency)
        if not self.winner_selection_seed:
            self.winner_selection_seed = generate_seed()
        super().save(*args, **kwargs)


class Entry(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="entries")
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name="entries")
    quantity = models.PositiveIntegerField(default=1, help_text="Number of entries this record represents")
    quantity_bonus = models.PositiveIntegerField(default=0, help_text="Number of bonus entries this record represents")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'raffle']]

    def __str__(self):
        if self.quantity > 1:
            return f"{self.user} → {self.raffle} (x{self.quantity})"
        return f"{self.user} → {self.raffle}"


class Winner(models.Model):
    raffle = models.OneToOneField(Raffle, on_delete=models.CASCADE, related_name="winner")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} won {self.raffle}"
