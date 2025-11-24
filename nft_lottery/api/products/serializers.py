from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from payments.models import CreditTransaction, TokenTransaction
from products.models import Product
from users.models import User


class ProductPurchaseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(read_only=True)
    credits_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tokens_added = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    credit_transaction_id = serializers.IntegerField(read_only=True)
    token_transaction_id = serializers.IntegerField(read_only=True)
    credit_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    token_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist as exc:
            raise serializers.ValidationError("Product not found.") from exc

        self.context["product"] = product
        return value

    def validate(self, attrs):
        product: Product = self.context.get("product")
        user = self.context["request"].user

        if user.credit_balance < product.price_credits:
            raise serializers.ValidationError("Insufficient credits to purchase the product.")

        return attrs

    def create(self, validated_data):
        product: Product = self.context["product"]
        request_user: User = self.context["request"].user

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=request_user.pk)

            if user.credit_balance < product.price_credits:
                raise serializers.ValidationError("Insufficient credits to purchase the product.")

            credit_transaction = CreditTransaction.objects.create(
                user=user,
                amount=product.price_credits,
                type="spend",
                meta={"product_id": product.id, "product_name": product.name},
            )

            token_transaction = TokenTransaction.objects.create(
                user=user,
                amount=product.reward_tokens,
                type="purchase",
                meta={"product_id": product.id, "product_name": product.name},
            )

            user.credit_balance = (user.credit_balance - product.price_credits).quantize(Decimal("0.01"))
            user.token_balance = (user.token_balance + product.reward_tokens).quantize(Decimal("0.01"))
            user.save(update_fields=["credit_balance", "token_balance"])

        return {
            "product_id": product.id,
            "product_name": product.name,
            "credits_spent": product.price_credits,
            "tokens_added": product.reward_tokens,
            "credit_transaction_id": credit_transaction.id,
            "token_transaction_id": token_transaction.id,
            "credit_balance": user.credit_balance,
            "token_balance": user.token_balance,
        }

