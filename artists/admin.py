from django.contrib import admin
from django.utils.html import format_html
from .models import ArtistProfile, Reel, ReelView, ReelLike, Follow

@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ['stage_name', 'user', 'genre', 'is_verified', 'is_featured', 'follower_count', 'reel_count', 'created_at']
    list_filter = ['is_verified', 'is_featured', 'genre', 'created_at']
    search_fields = ['stage_name', 'user__email', 'bio', 'genre']
    readonly_fields = ['created_at', 'updated_at', 'follower_count', 'reel_count', 'total_views', 'total_likes']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'stage_name', 'slug', 'bio', 'genre')
        }),
        ('Media', {
            'fields': ('profile_image', 'cover_image')
        }),
        ('Social Links', {
            'fields': ('instagram_handle', 'twitter_handle', 'tiktok_handle', 'youtube_channel', 'spotify_link', 'apple_music_link')
        }),
        ('Contact', {
            'fields': ('booking_email', 'phone_number')
        }),
        ('Settings', {
            'fields': ('is_verified', 'is_featured')
        }),
        ('Analytics', {
            'fields': ('follower_count', 'reel_count', 'total_views', 'total_likes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reel_count(self, obj):
        return obj.reels.count()
    reel_count.short_description = 'Reels'

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'content_type', 'status', 'view_count', 'like_count', 'created_at']
    list_filter = ['content_type', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'artist__stage_name']
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'like_count', 'share_count', 'download_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('artist', 'title', 'slug', 'description', 'content_type')
        }),
        ('Media Files', {
            'fields': ('video_file', 'image_file', 'thumbnail', 'duration')
        }),
        ('Settings', {
            'fields': ('allow_comments', 'allow_downloads', 'is_featured', 'status')
        }),
        ('Analytics', {
            'fields': ('view_count', 'like_count', 'share_count', 'download_count'),
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
        # Artists can only see their own reels
        try:
            artist_profile = request.user.artist_profile
            return qs.filter(artist=artist_profile)
        except ArtistProfile.DoesNotExist:
            return qs.none()

@admin.register(ReelView)
class ReelViewAdmin(admin.ModelAdmin):
    list_display = ['reel', 'user', 'viewed_at', 'ip_address']
    list_filter = ['viewed_at']
    search_fields = ['reel__title', 'user__email']
    readonly_fields = ['reel', 'user', 'ip_address', 'user_agent', 'viewed_at']

@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    list_display = ['reel', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['reel__title', 'user__email']
    readonly_fields = ['created_at']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['artist', 'follower', 'created_at']
    list_filter = ['created_at']
    search_fields = ['artist__stage_name', 'follower__email']
    readonly_fields = ['created_at']