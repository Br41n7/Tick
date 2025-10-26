from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('paystack', 'Paystack'),
        ('transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    TRANSACTION_TYPES = [
        ('booking', 'Event Booking'),
        ('commission', 'Commission Payment'),
        ('payout', 'Host Payout'),
        ('refund', 'Refund'),
    ]

    reference = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paystack')
    paystack_reference = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related objects
    booking = models.ForeignKey('events.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            self.reference = f"TXN{uuid.uuid4().hex[:16].upper()}"
        if self.status == 'success' and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.user.username} - {self.amount}"

class Commission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('calculated', 'Calculated'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='commission')
    booking = models.ForeignKey('events.Booking', on_delete=models.CASCADE, related_name='commissions')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='commissions')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions_earned')
    
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission percentage")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    host_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.commission_rate and self.booking_amount:
            self.commission_amount = (self.booking_amount * self.commission_rate) / Decimal('100')
            self.host_earnings = self.booking_amount - self.commission_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commission for {self.booking.reference} - {self.commission_amount}"

class Payout(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack Transfer'),
    ]

    reference = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payouts')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_deducted = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='bank_transfer')
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processor_reference = models.CharField(max_length=100, blank=True, null=True)
    processor_response = models.JSONField(default=dict, blank=True)
    
    description = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            self.reference = f"PAYOUT{uuid.uuid4().hex[:12].upper()}"
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        if self.status in ['processing', 'completed'] and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payout {self.reference} - {self.host.username} - {self.net_amount}"

class PayoutItem(models.Model):
    payout = models.ForeignKey(Payout, on_delete=models.CASCADE, related_name='items')
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='payout_items')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['payout', 'commission']

    def __str__(self):
        return f"{self.payout.reference} - {self.commission.booking.reference}"