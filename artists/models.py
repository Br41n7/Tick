from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()

class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    stage_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    bio = models.TextField()
    genre = models.CharField(max_length=100, help_text="Music genre (e.g., Afrobeats, Hip-hop, R&B)")
    
    profile_image = models.ImageField(upload_to='artist_profiles/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='artist_covers/', blank=True, null=True)
    
    # Social links
    instagram_handle = models.CharField(max_length=50, blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    tiktok_handle = models.CharField(max_length=50, blank=True)
    youtube_channel = models.URLField(blank=True)
    spotify_link = models.URLField(blank=True)
    apple_music_link = models.URLField(blank=True)
    
    # Contact info
    booking_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Analytics
    follower_count = models.PositiveIntegerField(default=0)
    reel_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.stage_name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('artists:artist_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.stage_name

class Reel(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('image', 'Image'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='reels')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='video')
    
    # Media files
    video_file = models.FileField(upload_to='reels/videos/', blank=True, null=True)
    image_file = models.ImageField(upload_to='reels/images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True)
    
    duration = models.PositiveIntegerField(help_text="Duration in seconds", default=0)
    
    # Settings
    allow_comments = models.BooleanField(default=True)
    allow_downloads = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('artists:reel_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.artist.stage_name} - {self.title}"

class ReelView(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_reels', null=True, blank=True)
    
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['reel', 'viewed_at']),
        ]

    def __str__(self):
        return f"View of {self.reel.title}"

class ReelLike(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_reels')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reel', 'user']

    def __str__(self):
        return f"{self.user.username} likes {self.reel.title}"

class Follow(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_artists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['artist', 'follower']
        indexes = [
            models.Index(fields=['artist', 'created_at']),
            models.Index(fields=['follower', 'created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.artist.stage_name}"