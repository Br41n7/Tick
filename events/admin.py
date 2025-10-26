from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import EventCategory, Event, Booking, EventFavorite, EventShare

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'category', 'status', 'start_date', 'ticket_price', 'sold_tickets', 'view_count']
    list_filter = ['status', 'is_featured', 'is_free', 'category', 'start_date']
    search_fields = ['title', 'description', 'venue_name', 'host__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'favorite_count', 'share_count', 'sold_tickets']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'host', 'category')
        }),
        ('Venue Details', {
            'fields': ('venue_name', 'venue_address', 'city', 'state', 'country')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date')
        }),
        ('Pricing', {
            'fields': ('ticket_price', 'available_tickets', 'is_free')
        }),
        ('Media', {
            'fields': ('image', 'featured_image')
        }),
        ('Settings', {
            'fields': ('is_featured', 'status')
        }),
        ('Analytics', {
            'fields': ('view_count', 'favorite_count', 'share_count', 'sold_tickets'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Non-superusers can only see their own events
        return qs.filter(host=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            if not request.user.is_superuser and obj.host != request.user:
                return ['host']  # Can't change the host if it's not your event
            return self.readonly_fields
        return []

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'event', 'user', 'quantity', 'total_price', 'status', 'booked_at']
    list_filter = ['status', 'booked_at', 'event__category']
    search_fields = ['booking_reference', 'event__title', 'user__email', 'customer_name']
    readonly_fields = ['booking_reference', 'booked_at', 'updated_at']
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('booking_reference', 'event', 'user', 'quantity', 'unit_price', 'total_price')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Payment', {
            'fields': ('payment_reference', 'status')
        }),
        ('Additional', {
            'fields': ('notes', 'booked_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Hosts can only see bookings for their events
        return qs.filter(event__host=request.user)

@admin.register(EventFavorite)
class EventFavoriteAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['event__title', 'user__email']
    readonly_fields = ['created_at']

@admin.register(EventShare)
class EventShareAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'platform', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['event__title', 'user__email']
    readonly_fields = ['share_url', 'ip_address', 'user_agent', 'created_at']