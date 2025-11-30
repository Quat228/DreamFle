from django.urls import path
from .views import (
    CRMLoginView,
    CRMUserView,
    RaffleListForCRMView,
    RaffleDetailForCRMView,
    UpdateRaffleStartTimeView
)

app_name = 'crm'

urlpatterns = [
    path('auth/login/', CRMLoginView.as_view(), name='crm-auth-login'),
    path('auth/me/', CRMUserView.as_view(), name='crm-auth-me'),
    path('raffles/', RaffleListForCRMView.as_view(), name='raffle-list'),
    path('raffles/<int:raffle_id>/', RaffleDetailForCRMView.as_view(), name='raffle-detail'),
    path(
        'raffles/<int:raffle_id>/update-start-time/',
        UpdateRaffleStartTimeView.as_view(),
        name='update-raffle-start-time'
    ),
]

