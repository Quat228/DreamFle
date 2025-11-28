from django.urls import path
from .views import (
    RaffleListAPIView,
    RaffleDetailAPIView,
    RaffleEnterAPIView,
    MyEntriesAPIView,
    RaffleTransparencyAPIView,
)

urlpatterns = [
    path("raffles/", RaffleListAPIView.as_view(), name="raffle-list"),
    path("raffles/<int:id>/", RaffleDetailAPIView.as_view(), name="raffle-detail"),
    path("raffles/<int:id>/enter/", RaffleEnterAPIView.as_view(), name="raffle-enter"),
    path("raffles/<int:id>/transparency/", RaffleTransparencyAPIView.as_view(), name="raffle-transparency"),
    path("entries/", MyEntriesAPIView.as_view(), name="my-entries"),
]



