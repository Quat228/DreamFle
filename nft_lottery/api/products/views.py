from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.lottery.serializers import EntrySerializer

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
    Purchase a product and grant entries to a raffle.
    Request body should include: {"raffle_id": <raffle_id>}
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

        # Get raffle_id from request body or query parameter
        raffle_id = request.data.get('raffle_id') or request.query_params.get('raffle_id')
        
        if not raffle_id:
            return Response(
                {"detail": "raffle_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            raffle_id = int(raffle_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "raffle_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = purchase_product(request.user, product, raffle_id)

            return Response({
                "detail": f"Purchase successful! You received {result['entries_granted']} entries.",
                "product": ProductSerializer(product).data,
                "entry": EntrySerializer(result["entry"]).data,
                "entries_granted": result["entries_granted"],
                "total_entries": result["total_entries"],
                "raffle_id": result["raffle_id"],
                "raffle_name": result["raffle_name"],
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
