from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, RoleUpgradeRequest


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = ['email', 'username', 'get_display_role', 'is_artist', 'is_host', 
                    'is_staff', 'created_at']
    list_filter = ['role', 'is_artist', 'is_host', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('phone_number', 'avatar', 'bio')
        }),
        ('Role Management', {
            'fields': ('role', 'is_artist', 'is_host')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['make_artist', 'make_host', 'make_both']
    
    def make_artist(self, request, queryset):
        """Admin action to upgrade users to artist."""
        for user in queryset:
            user.upgrade_to_artist()
        self.message_user(request, f"{queryset.count()} users upgraded to Artist.")
    make_artist.short_description = "Upgrade to Artist"
    
    def make_host(self, request, queryset):
        """Admin action to upgrade users to host."""
        for user in queryset:
            user.upgrade_to_host()
        self.message_user(request, f"{queryset.count()} users upgraded to Host.")
    make_host.short_description = "Upgrade to Host"
    
    def make_both(self, request, queryset):
        """Admin action to give users both roles."""
        for user in queryset:
            user.upgrade_to_artist()
            user.upgrade_to_host()
        self.message_user(request, f"{queryset.count()} users upgraded to Artist & Host.")
    make_both.short_description = "Upgrade to Artist & Host"


@admin.register(RoleUpgradeRequest)
class RoleUpgradeRequestAdmin(admin.ModelAdmin):
    """Admin for role upgrade requests."""
    
    list_display = ['user', 'request_type', 'status', 'created_at']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['user__email', 'user__username', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'request_type', 'reason', 'status')
        }),
        ('Admin Response', {
            'fields': ('admin_notes', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Approve selected upgrade requests."""
        count = 0
        for upgrade_request in queryset.filter(status='pending'):
            upgrade_request.approve(request.user)
            count += 1
        self.message_user(request, f"{count} requests approved.")
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        """Reject selected upgrade requests."""
        count = 0
        for upgrade_request in queryset.filter(status='pending'):
            upgrade_request.reject(request.user)
            count += 1
        self.message_user(request, f"{count} requests rejected.")
    reject_requests.short_description = "Reject selected requests"