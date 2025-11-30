from django.urls import path
from .views import TelegramAuthView, CustomTokenRefreshView

urlpatterns = [
    path("telegram/", TelegramAuthView.as_view()),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
