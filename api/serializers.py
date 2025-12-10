from rest_framework import serializers
from django.contrib.auth import get_user_model
from events.models import Event, Booking
from accounts.models import RoleUpgradeRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_artist', 'is_host']
        read_only_fields = ['id', 'is_artist', 'is_host']

class EventSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'short_description', 'host', 'start_date', 'end_date', 'ticket_price', 'available_tickets', 'status']
        read_only_fields = ['id', 'slug']

class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_reference', 'event', 'user', 'quantity', 'unit_price', 'total_price', 'status', 'booked_at']
        read_only_fields = ['id', 'booking_reference', 'total_price', 'booked_at']

class RoleUpgradeRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoleUpgradeRequest
        fields = ['id', 'user', 'request_type', 'reason', 'kyc_status', 'created_at']
        read_only_fields = ['id', 'user', 'kyc_status', 'created_at']
