from django.urls import path
from .views import (
    RaffleListAPIView,
    RaffleDetailAPIView,
    MyEntriesAPIView,
    RaffleTransparencyAPIView,
    PreviousRafflesAPIView,
)

urlpatterns = [
    path("raffles/", RaffleListAPIView.as_view(), name="raffle-list"),
    path("raffles/previous/", PreviousRafflesAPIView.as_view(), name="previous-raffles"),
    path("raffles/<int:id>/", RaffleDetailAPIView.as_view(), name="raffle-detail"),
    path("raffles/<int:id>/transparency/", RaffleTransparencyAPIView.as_view(), name="raffle-transparency"),
    path("entries/", MyEntriesAPIView.as_view(), name="my-entries"),
]



