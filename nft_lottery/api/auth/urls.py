from django.urls import path
from .views import TelegramAuthView

urlpatterns = [
    path("telegram/", TelegramAuthView.as_view()),
]
