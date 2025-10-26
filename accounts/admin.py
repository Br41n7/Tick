from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, RoleUpgradeRequest

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'get_display_role', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_artist', 'is_host', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'bio')}),
        (_('Role Settings'), {
            'fields': ('role', 'is_artist', 'is_host'),
            'description': 'Configure user roles. Users can have multiple roles (artist + host).'
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']

@admin.register(RoleUpgradeRequest)
class RoleUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'request_type', 'status', 'created_at', 'processed_by']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['user__email', 'reason', 'admin_notes']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_requests', 'reject_requests']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'request_type', 'reason')
        }),
        ('Admin Response', {
            'fields': ('status', 'processed_by', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_requests(self, request, queryset):
        count = 0
        for upgrade_request in queryset.filter(status='pending'):
            upgrade_request.approve(request.user)
            count += 1
        self.message_user(request, f'{count} upgrade requests approved.')
    approve_requests.short_description = 'Approve selected requests'
    
    def reject_requests(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} upgrade requests rejected.')
    reject_requests.short_description = 'Reject selected requests'