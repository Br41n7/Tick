from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Transaction, Commission, Payout, PayoutItem

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'transaction_type', 'user', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['transaction_type', 'status', 'payment_method', 'created_at']
    search_fields = ['reference', 'user__email', 'description']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('reference', 'transaction_type', 'user', 'amount', 'description')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'paystack_reference', 'status')
        }),
        ('Related Objects', {
            'fields': ('booking',)
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'host', 'event', 'booking_amount', 'commission_amount', 'host_earnings', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking__reference', 'host__email', 'event__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def booking_reference(self, obj):
        return obj.booking.reference
    booking_reference.short_description = 'Booking Ref'
    
    fieldsets = (
        ('Commission Details', {
            'fields': ('transaction', 'booking', 'event', 'host')
        }),
        ('Financial Breakdown', {
            'fields': ('booking_amount', 'commission_rate', 'commission_amount', 'host_earnings')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['reference', 'host', 'total_amount', 'commission_deducted', 'net_amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'payment_method', 'created_at', 'completed_at']
    search_fields = ['reference', 'host__email']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'processed_at', 'completed_at']
    
    fieldsets = (
        ('Payout Details', {
            'fields': ('reference', 'host', 'total_amount', 'commission_deducted', 'net_amount')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'bank_name', 'account_name', 'account_number')
        }),
        ('Status Tracking', {
            'fields': ('status', 'processor_reference', 'description')
        }),
        ('Processor Response', {
            'fields': ('processor_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PayoutItem)
class PayoutItemAdmin(admin.ModelAdmin):
    list_display = ['payout_reference', 'commission_booking', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['payout__reference', 'commission__booking__reference']
    readonly_fields = ['created_at']
    
    def payout_reference(self, obj):
        return obj.payout.reference
    payout_reference.short_description = 'Payout Ref'
    
    def commission_booking(self, obj):
        return obj.commission.booking.reference
    commission_booking.short_description = 'Booking Ref'