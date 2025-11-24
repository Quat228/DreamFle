from django.urls import path

from .views import ProductPurchaseAPIView

urlpatterns = [
    path("purchase/", ProductPurchaseAPIView.as_view(), name="product-purchase"),
]


