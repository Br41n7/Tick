from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SiteConfiguration(models.Model):
    """Global site settings"""
    site_name = models.CharField(max_length=100, default="Tick Entertainment")
    site_description = models.TextField(default="Your premier entertainment and event booking platform")
    
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    
    contact_email = models.EmailField(default="info@tick.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    
    social_facebook = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_youtube = models.URLField(blank=True)
    
    # Commission settings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, 
                                       help_text="Commission percentage charged to hosts")
    
    # Payment settings
    paystack_public_key = models.CharField(max_length=100, blank=True)
    paystack_secret_key = models.CharField(max_length=100, blank=True)
    paystack_test_mode = models.BooleanField(default=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name

class ActivityLog(models.Model):
    """Track user activities across the platform"""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('booking', 'Event Booking'),
        ('payment', 'Payment'),
        ('follow', 'Follow Artist'),
        ('favorite', 'Favorite Event'),
        ('share', 'Share Content'),
        ('upload', 'Upload Content'),
        ('profile_update', 'Profile Update'),
        ('role_request', 'Role Upgrade Request'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    description = models.TextField()
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.created_at}"

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('follow', 'Follow'),
        ('favorite', 'Favorite'),
        ('share', 'Share'),
        ('system', 'System'),
        ('role_approval', 'Role Approval'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', 
                              null=True, blank=True)
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

class ContactMessage(models.Model):
    """Contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    
    category = models.CharField(max_length=100, default='General')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question