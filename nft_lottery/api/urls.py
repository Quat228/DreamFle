from django.urls import path, include

urlpatterns = [
    path("auth/", include("api.auth.urls")),
    path("users/", include("api.users.urls")),
    path("products/", include("api.products.urls")),
    path("lottery/", include("api.lottery.urls")),
    path("crm/", include("crm.urls")),
]
