from django.db import models

RARITY_CHOICES = (
        ("common", "Common"),
        ("uncommon", "Uncommon"),
        ("rare", "Rare"),
        ("epic", "Epic"),
        ("legendary", "Legendary"),
    )


class ProductType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type = models.ForeignKey(ProductType, on_delete=models.PROTECT, related_name="products")
    price_credits = models.DecimalField(max_digits=12, decimal_places=2)
    reward_tokens = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.URLField(max_length=2000, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} [{self.type}]"


class PrizeType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Prize(models.Model):
    type = models.ForeignKey(PrizeType, on_delete=models.PROTECT, related_name="prizes")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=2000, null=True, blank=True)
    rarity = models.CharField(
        max_length=20,
        choices=RARITY_CHOICES,
        default="common"
    )
    value_estimate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"
