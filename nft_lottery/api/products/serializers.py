from rest_framework import serializers
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="type.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "type_name",
            "price",
            "entries_per_product",
            "image",
        )
        read_only_fields = fields
