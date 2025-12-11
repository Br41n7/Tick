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


class BookingCreateSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Booking
        fields = ['id', 'event_id', 'quantity', 'customer_name', 'customer_email', 'customer_phone', 'notes']
        read_only_fields = ['id']

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(pk=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError('Event not found')
        if event.is_sold_out:
            raise serializers.ValidationError('Event is sold out')
        return value

    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        event = Event.objects.get(pk=event_id)
        user = self.context['request'].user
        quantity = validated_data.get('quantity', 1)

        booking = Booking(
            event=event,
            user=user,
            quantity=quantity,
            unit_price=event.ticket_price,
            customer_name=validated_data.get('customer_name', user.get_full_name() or user.email),
            customer_email=validated_data.get('customer_email', user.email),
            customer_phone=validated_data.get('customer_phone', ''),
            notes=validated_data.get('notes', ''),
        )
        booking.save()
        return booking

class RoleUpgradeRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RoleUpgradeRequest
        fields = ['id', 'user', 'request_type', 'reason', 'kyc_status', 'created_at']
        read_only_fields = ['id', 'user', 'kyc_status', 'created_at']


class RoleUpgradeRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleUpgradeRequest
        fields = ['id', 'request_type', 'reason', 'kyc_id_type', 'kyc_id_number', 'kyc_document']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        req = RoleUpgradeRequest.objects.create(user=user, **validated_data)
        return req
