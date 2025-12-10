from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model with role-based access.
    Roles: ordinary_user, artist, host, admin
    """
    
    ROLE_CHOICES = [
        ('ordinary_user', 'Ordinary User'),
        ('artist', 'Artist'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # Role management
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='ordinary_user'
    )
    
    # Additional roles (for dual role support)
    is_artist = models.BooleanField(default=False)
    is_host = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip() or self.email
    
    def can_create_events(self):
        """Check if user can create events (Host role)."""
        return self.is_host or self.role == 'host' or self.is_superuser
    
    def can_upload_reels(self):
        """Check if user can upload reels (Artist role)."""
        return self.is_artist or self.role == 'artist' or self.is_superuser
    
    def upgrade_to_artist(self):
        """Upgrade user to artist role."""
        self.is_artist = True
        if self.role == 'ordinary_user':
            self.role = 'artist'
        self.save()
    
    def upgrade_to_host(self):
        """Upgrade user to host role."""
        self.is_host = True
        if self.role == 'ordinary_user':
            self.role = 'host'
        elif self.role == 'artist':
            # Artist can also be host (dual role)
            pass
        self.save()
    
    def has_dual_role(self):
        """Check if user has both artist and host roles."""
        return self.is_artist and self.is_host
    
    def get_display_role(self):
        """Get display-friendly role name."""
        if self.is_superuser:
            return 'Super Admin'
        elif self.has_dual_role():
            return 'Artist & Host'
        elif self.is_host:
            return 'Host'
        elif self.is_artist:
            return 'Artist'
        else:
            return 'User'


class RoleUpgradeRequest(models.Model):
    """
    Model to track role upgrade requests.
    """
    
    REQUEST_TYPE_CHOICES = [
        ('to_artist', 'Upgrade to Artist'),
        ('to_host', 'Upgrade to Host'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='upgrade_requests'
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(help_text="Why do you want this upgrade?")

    # KYC fields (uploaded by the user as part of upgrade request)
    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    kyc_id_type = models.CharField(max_length=50, blank=True, null=True)
    kyc_id_number = models.CharField(max_length=100, blank=True, null=True)
    kyc_document = models.FileField(upload_to='kyc_docs/', blank=True, null=True)
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='pending')
    kyc_submitted_at = models.DateTimeField(blank=True, null=True)
    kyc_verified_at = models.DateTimeField(blank=True, null=True)
    kyc_reject_reason = models.TextField(blank=True, null=True)

    # Admin response
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_requests'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_request_type_display()} ({self.status})"
    
    def approve(self, admin_user):
        """Approve the upgrade request."""
        # Require KYC verification before approving
        if getattr(self, 'kyc_status', None) != 'verified':
            raise ValueError('KYC must be verified before approving this request.')

        self.status = 'approved'
        self.processed_by = admin_user
        self.save()

        # Upgrade the user
        if self.request_type == 'to_artist':
            self.user.upgrade_to_artist()
        elif self.request_type == 'to_host':
            self.user.upgrade_to_host()

    def verify_kyc(self, admin_user, verified=True, notes=''):
        """Admin verifies or rejects KYC for this request."""
        if verified:
            self.kyc_status = 'verified'
            from django.utils import timezone
            self.kyc_verified_at = timezone.now()
            self.admin_notes = notes or self.admin_notes
            self.processed_by = admin_user
            self.save()
        else:
            self.kyc_status = 'rejected'
            self.kyc_reject_reason = notes
            self.processed_by = admin_user
            self.save()
    
    def reject(self, admin_user, notes=''):
        """Reject the upgrade request."""
        self.status = 'rejected'
        self.processed_by = admin_user
        self.admin_notes = notes
        self.save()


class KycAuditLog(models.Model):
    """Audit log for KYC and role request actions."""
    ACTION_CHOICES = [
        ('kyc_verified', 'KYC Verified'),
        ('kyc_rejected', 'KYC Rejected'),
        ('role_approved', 'Role Approved'),
        ('role_rejected', 'Role Rejected'),
    ]

    request = models.ForeignKey(RoleUpgradeRequest, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    admin = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request.user.email} - {self.get_action_display()} @ {self.created_at}"