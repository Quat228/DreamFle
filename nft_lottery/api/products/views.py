from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from products.models import Product
from products.services import purchase_product
from .serializers import ProductSerializer


class ProductDetailAPIView(RetrieveAPIView):
    """
    GET /api/products/<id>/
    Returns one product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class ProductListAPIView(ListAPIView):
    """
    GET /api/products/
    Return list of active products.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]


class ProductPurchaseAPIView(APIView):
    """
    POST /api/products/<id>/purchase/
    Purchase a product using credits.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            result = purchase_product(request.user, product)
            
            return Response({
                "detail": "Purchase successful",
                "product": ProductSerializer(product).data,
                "new_credit_balance": result["new_credit_balance"],
                "new_token_balance": result["new_token_balance"],
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
