from django.urls import path
from .views import ProductListAPIView, ProductDetailAPIView, ProductPurchaseAPIView

urlpatterns = [
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("<int:id>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("<int:id>/purchase/", ProductPurchaseAPIView.as_view(), name="product-purchase"),
]