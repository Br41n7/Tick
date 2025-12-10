from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from events.models import Event, Booking
from accounts.models import RoleUpgradeRequest
from .serializers import UserSerializer, EventSerializer, BookingSerializer, RoleUpgradeRequestSerializer

User = get_user_model()

class PublicEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(status='published')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.all().select_related('event', 'user')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all().select_related('event', 'user')
        return Booking.objects.filter(user=user).select_related('event', 'user')

class RoleUpgradeRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoleUpgradeRequest.objects.all().select_related('user')
    serializer_class = RoleUpgradeRequestSerializer
    permission_classes = [permissions.IsAdminUser]
