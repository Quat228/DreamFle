from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from .frontend_view import miniapp, crm_app


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Catch all CRM routes - serve React app for all /crm/* paths
    re_path(r'^crm/.*$', crm_app, name="crm"),
    path("", miniapp, name="miniapp"),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
