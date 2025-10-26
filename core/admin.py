from django.contrib import admin
from .models import SiteConfiguration, ActivityLog, Notification, ContactMessage, FAQ

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'commission_rate', 'maintenance_mode', 'updated_at']
    search_fields = ['site_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Settings', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Social Media', {
            'fields': ('social_facebook', 'social_twitter', 'social_instagram', 'social_youtube')
        }),
        ('Financial Settings', {
            'fields': ('commission_rate',)
        }),
        ('Payment Settings', {
            'fields': ('paystack_public_key', 'paystack_secret_key', 'paystack_test_mode')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'description', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__email', 'description']
    readonly_fields = ['user', 'action_type', 'description', 'object_id', 'object_type', 'ip_address', 'user_agent', 'created_at']
    
    def has_add_permission(self, request):
        return False  # Activity logs should not be manually added

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__email', 'sender__email', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'sender', 'notification_type', 'title', 'message')
        }),
        ('Link', {
            'fields': ('url',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Object Reference', {
            'fields': ('object_id', 'object_type'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'replied', 'created_at']
    list_filter = ['is_read', 'replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'ip_address', 'user_agent', 'created_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'replied')
        }),
        ('Technical Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Contact messages should not be manually added

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'category']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('FAQ Details', {
            'fields': ('question', 'answer', 'category')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )