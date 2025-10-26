from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()

class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Event Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=200, help_text="Brief description for listings")
    
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_events')
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    
    venue_name = models.CharField(max_length=200)
    venue_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField(default=0)
    sold_tickets = models.PositiveIntegerField(default=0)
    
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    featured_image = models.ImageField(upload_to='event_featured/', blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Analytics fields
    view_count = models.PositiveIntegerField(default=0)
    favorite_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_free:
            self.ticket_price = 0
        super().save(*args, **kwargs)

    @property
    def available_tickets_count(self):
        return max(0, self.available_tickets - self.sold_tickets)

    @property
    def is_sold_out(self):
        return self.available_tickets_count == 0

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_date > timezone.now()

    @property
    def is_past(self):
        from django.utils import timezone
        return self.end_date < timezone.now()

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    booking_reference = models.CharField(max_length=20, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    notes = models.TextField(blank=True)
    
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booked_at']
        unique_together = ['event', 'user', 'booking_reference']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"EV{uuid.uuid4().hex[:12].upper()}"
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} - {self.event.title} ({self.quantity} tickets)"

class EventFavorite(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class EventShare(models.Model):
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('email', 'Email'),
        ('copy_link', 'Copy Link'),
        ('other', 'Other'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_events', null=True, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    share_url = models.URLField(max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform} - {self.event.title}"