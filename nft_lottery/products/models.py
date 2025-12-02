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
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in real money")
    entries_per_product = models.PositiveIntegerField(help_text="Number of entries granted per purchase")
    image = models.ImageField(upload_to='products/', null=True, blank=True)
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
    image = models.ImageField(upload_to='prizes/', null=True, blank=True)
    rarity = models.CharField(
        max_length=20,
        choices=RARITY_CHOICES,
        default="common"
    )
    value_estimate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"
