from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth import get_user_model
from events.models import Event, Booking
from accounts.models import RoleUpgradeRequest
from .serializers import (
    UserSerializer,
    EventSerializer,
    BookingSerializer,
    RoleUpgradeRequestSerializer,
    BookingCreateSerializer,
    RoleUpgradeRequestCreateSerializer,
)

User = get_user_model()

class PublicEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(status='published')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BookingViewSet(viewsets.ModelViewSet):
    """Bookings: users can create bookings, view their own bookings; admins can view all."""
    queryset = Booking.objects.all().select_related('event', 'user')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create']:
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all().select_related('event', 'user')
        return Booking.objects.filter(user=user).select_related('event', 'user')

    def perform_create(self, serializer):
        # serializer.create handles event lookup and user assignment
        serializer.save()

    @extend_schema(
        request=BookingCreateSerializer,
        responses={201: BookingSerializer},
        description="Create a booking for an event. Auth required.",
        examples=[
            OpenApiExample(
                'Example Booking',
                summary='Create a booking',
                value={
                    'event_id': 1,
                    'quantity': 2,
                    'customer_name': 'Jane Doe',
                    'customer_email': 'jane@example.com',
                    'customer_phone': '+1234567890',
                    'notes': 'Seat near stage'
                },
                request_only=True,
                response_only=False,
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class RoleUpgradeRequestViewSet(viewsets.ModelViewSet):
    """Role upgrade requests: users can create, admins can list/manage."""
    queryset = RoleUpgradeRequest.objects.all().select_related('user')

    def get_serializer_class(self):
        if self.action in ['create']:
            return RoleUpgradeRequestCreateSerializer
        return RoleUpgradeRequestSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        request=RoleUpgradeRequestCreateSerializer,
        responses={201: RoleUpgradeRequestSerializer},
        description="Submit a role upgrade request with optional KYC documents.",
        examples=[
            OpenApiExample(
                'Upgrade to Artist',
                summary='Artist request example',
                value={
                    'request_type': 'to_artist',
                    'reason': 'I create music and want to list shows',
                    'kyc_id_type': 'Passport',
                    'kyc_id_number': 'A1234567',
                    # 'kyc_document': <file upload in multipart/form-data>
                },
                request_only=True,
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
