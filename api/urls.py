from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicEventViewSet, UserViewSet, BookingViewSet, RoleUpgradeRequestViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'events', PublicEventViewSet, basename='events')
router.register(r'users', UserViewSet, basename='users')
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'role-requests', RoleUpgradeRequestViewSet, basename='role-requests')

urlpatterns = [
    path('', include(router.urls)),

    # Schema and docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
