from django.urls import path
from .views import MeAPIView, UserReferralsAPIView

urlpatterns = [
    path("me/", MeAPIView.as_view(), name="user-me"),
    path("referrals/", UserReferralsAPIView.as_view(), name="user-referrals"),
]
