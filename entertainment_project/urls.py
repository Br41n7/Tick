"""
URL configuration for entertainment_project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('events/', include('events.urls')),
    path('artists/', include('artists.urls')),
    path('payments/', include('payments.urls')),
    path('user/', include('accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Entertainment Platform Admin"
admin.site.site_title = "Entertainment Platform"
admin.site.index_title = "Welcome to Entertainment Platform Administration"