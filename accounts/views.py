from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import RoleUpgradeRequest
from .forms import UserProfileForm, RoleUpgradeRequestForm, LoginForm, SignUpForm
from .utils import send_html_email, audit_and_webhook
from events.models import Event, Booking, EventFavorite
from artists.models import ArtistProfile, Reel, Follow
from payments.models import Transaction, Commission
from django.utils import timezone

User = get_user_model()

def signup(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('accounts:user_dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('accounts:user_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                    
                    # Redirect to appropriate dashboard
                    return redirect('accounts:user_dashboard')
                else:
                    messages.error(request, 'Invalid password. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email. Please sign up.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')


def user_profile(request):
    """View user profile"""
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def user_dashboard(request):
    """User dashboard - redirects based on user role"""
    if request.user.is_superuser:
        return redirect('accounts:admin_dashboard')
    elif request.user.is_host:
        return redirect('accounts:host_dashboard')
    elif request.user.is_artist:
        return redirect('accounts:artist_dashboard')
    else:
        # Regular user dashboard
        recent_bookings = request.user.bookings.all().order_by('-booked_at')[:5]
        favorite_events = request.user.favorite_events.all().order_by('-created_at')[:5]
        
        # Get popular reels
        popular_reels = Reel.objects.filter(status='published').order_by('-view_count')[:6]
        
        # Get featured artists
        featured_artists = ArtistProfile.objects.filter(is_featured=True).order_by('-follower_count')[:6]
        
        # Get artists user is following
        following_count = request.user.following_artists.count() if hasattr(request.user, 'following_artists') else 0
        
        context = {
            'recent_bookings': recent_bookings,
            'favorite_events': favorite_events,
            'popular_reels': popular_reels,
            'featured_artists': featured_artists,
            'following_count': following_count,
        }
        return render(request, 'accounts/dashboard.html', context)

@login_required
def my_bookings(request):
    """View user's bookings"""
    bookings = request.user.bookings.all().order_by('-booked_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/my_bookings.html', context)

@login_required
def booking_detail(request, reference):
    """View booking details"""
    booking = get_object_or_404(Booking, booking_reference=reference, user=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'accounts/booking_detail.html', context)

@login_required
def my_favorites(request):
    """View user's favorite events"""
    favorites = request.user.favorite_events.all().order_by('-created_at')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'accounts/my_favorites.html', context)

@login_required
def my_following(request):
    """View artists user is following"""
    follows = request.user.following_artists.select_related('artist').order_by('-created_at')
    
    context = {
        'follows': follows,
    }
    return render(request, 'accounts/my_following.html', context)

@login_required
def request_role_upgrade(request):
    """Request role upgrade"""
    if request.method == 'POST':
        form = RoleUpgradeRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            upgrade_request = form.save(commit=False)
            upgrade_request.user = request.user
            # If KYC document uploaded, set submission timestamp and default kyc_status
            if form.cleaned_data.get('kyc_document'):
                upgrade_request.kyc_submitted_at = timezone.now()
                upgrade_request.kyc_status = 'pending'
            upgrade_request.save()

            messages.success(request, 'Role upgrade request submitted successfully! Admins will review your KYC and request.')
            return redirect('accounts:my_upgrade_requests')
    else:
        form = RoleUpgradeRequestForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/request_role_upgrade.html', context)

@login_required
def my_upgrade_requests(request):
    """View user's upgrade requests"""
    requests = request.user.upgrade_requests.all().order_by('-created_at')
    
    context = {
        'requests': requests,
    }
    return render(request, 'accounts/my_upgrade_requests.html', context)

@login_required
def artist_dashboard(request):
    """Artist dashboard"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to access artist dashboard!')
        return redirect('accounts:dashboard')
    
    try:
        artist_profile = request.user.artist_profile
    except ArtistProfile.DoesNotExist:
        artist_profile = None

    # If the user is allowed to upload reels but hasn't created an ArtistProfile yet,
    # redirect them to the artist profile setup page so they can complete their profile.
    if not artist_profile:
        messages.info(request, 'Please create your artist profile to access the artist dashboard.')
        return redirect('artists:edit_artist_profile')
    
    # Get artist's reels (use an empty QuerySet when no profile to keep API consistent)
    reels = artist_profile.reels.all().order_by('-created_at') if artist_profile else Reel.objects.none()
    total_reels = reels.count()
    published_reels = reels.filter(status='published').count()

    # Calculate statistics
    total_views = sum(reel.view_count for reel in reels) if reels else 0
    total_likes = sum(reel.like_count for reel in reels) if reels else 0
    follower_count = artist_profile.follower_count if artist_profile else 0
    
    context = {
        'artist_profile': artist_profile,
        'reels': reels[:5],
        'total_reels': total_reels,
        'published_reels': published_reels,
        'total_views': total_views,
        'total_likes': total_likes,
        'follower_count': follower_count,
    }
    return render(request, 'accounts/artist_dashboard.html', context)

@login_required
def host_dashboard(request):
    """Host dashboard"""
    if not request.user.can_create_events():
        messages.error(request, 'You do not have permission to access host dashboard!')
        return redirect('accounts:dashboard')
    
    events = request.user.hosted_events.all().order_by('-created_at')
    
    # Calculate statistics
    total_events = events.count()
    published_events = events.filter(status='published').count()
    total_bookings = Booking.objects.filter(event__host=request.user).count()
    confirmed_bookings = Booking.objects.filter(
        event__host=request.user,
        status='confirmed'
    ).count()
    
    # Calculate revenue
    total_revenue = Booking.objects.filter(
        event__host=request.user,
        status='confirmed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    context = {
        'events': events[:5],
        'total_events': total_events,
        'published_events': published_events,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
    }
    return render(request, 'accounts/host_dashboard.html', context)

@login_required
def my_events(request):
    """View user's events"""
    if not request.user.can_create_events():
        messages.error(request, 'You do not have permission to manage events!')
        return redirect('accounts:dashboard')
    
    events = request.user.hosted_events.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        events = events.filter(status=status_filter)
    
    context = {
        'events': events,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/my_events.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """Admin dashboard"""
    # Platform statistics
    total_users = User.objects.count()
    total_artists = User.objects.filter(is_artist=True).count()
    total_hosts = User.objects.filter(is_host=True).count()
    regular_users = total_users - total_artists - total_hosts
    total_events = Event.objects.count()
    published_events = Event.objects.filter(status='published').count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_events = Event.objects.order_by('-created_at')[:5]
    pending_requests = RoleUpgradeRequest.objects.filter(status='pending')
    
    context = {
        'total_users': total_users,
        'total_artists': total_artists,
        'total_hosts': total_hosts,
        'regular_users': regular_users,
        'total_events': total_events,
        'published_events': published_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_users': recent_users,
        'recent_events': recent_events,
        'pending_requests': pending_requests,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    """Manage all users"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search and filter
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    role_filter = request.GET.get('role', '')
    if role_filter == 'artist':
        users = users.filter(is_artist=True)
    elif role_filter == 'host':
        users = users.filter(is_host=True)
    elif role_filter == 'regular':
        users = users.filter(is_artist=False, is_host=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
    }
    return render(request, 'accounts/manage_users.html', context)

@user_passes_test(lambda u: u.is_superuser)
def view_user_profile(request, user_id):
    """View any user's profile (admin only)"""
    user = get_object_or_404(User, pk=user_id)
    
    # Get user stats
    bookings = user.bookings.count() if hasattr(user, 'bookings') else 0
    favorites = user.favorite_events.count() if hasattr(user, 'favorite_events') else 0
    following = user.following_artists.count() if hasattr(user, 'following_artists') else 0
    
    context = {
        'viewed_user': user,
        'bookings_count': bookings,
        'favorites_count': favorites,
        'following_count': following,
    }
    return render(request, 'accounts/admin_view_user.html', context)

@user_passes_test(lambda u: u.is_superuser)
def manage_role_requests(request):
    """Manage role upgrade requests"""
    requests = RoleUpgradeRequest.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
    }
    return render(request, 'accounts/manage_role_requests.html', context)

@login_required
def upgrade_role(request):
    """Upgrade user role from ordinary_user to artist/host"""
    if request.method == 'POST':
        role = request.POST.get('role', '').lower()
        if role not in ['artist', 'host']:
            messages.error(request, 'Invalid role selected.')
            return redirect('accounts:upgrade_role')
        
        # Create upgrade request (model uses `request_type` values 'to_artist' / 'to_host')
        from .models import RoleUpgradeRequest
        mapping = {
            'artist': 'to_artist',
            'host': 'to_host',
        }
        request_type = mapping.get(role)
        upgrade_request = RoleUpgradeRequest.objects.create(
            user=request.user,
            request_type=request_type,
            reason=request.POST.get('reason', ''),
            status='pending'
        )
        messages.success(request, f'Your {role} role upgrade request has been submitted. Admins will review it shortly.')
        return redirect('accounts:my_upgrade_requests')
    
    # Check if already artist or host
    if request.user.is_artist or request.user.is_host:
        messages.info(request, 'You already have an upgraded role.')
        return redirect('accounts:dashboard')
    
    context = {}
    return render(request, 'accounts/upgrade_role.html', context)


@login_required
def cancel_upgrade_request(request, pk):
    """Allow a user to cancel their pending role upgrade request."""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('accounts:my_upgrade_requests')

    req = get_object_or_404(RoleUpgradeRequest, pk=pk, user=request.user)
    if req.status != 'pending':
        messages.error(request, 'Only pending requests can be canceled.')
        return redirect('accounts:my_upgrade_requests')

    # Mark as rejected/canceled by user for audit trail
    req.status = 'rejected'
    req.admin_notes = (req.admin_notes or '') + '\nCanceled by user.'
    req.processed_by = request.user
    req.save()

    messages.success(request, 'Your upgrade request has been canceled.')
    return redirect('accounts:my_upgrade_requests')


@login_required
def upgrade_request_detail(request, pk):
    """Detailed view for a role upgrade request (owner or admin)."""
    req = get_object_or_404(RoleUpgradeRequest, pk=pk)
    # Only owner or superuser can view
    if not (request.user.is_superuser or req.user == request.user):
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('accounts:my_upgrade_requests')

    context = {
        'request_obj': req,
    }
    return render(request, 'accounts/upgrade_request_detail.html', context)

@login_required
def delete_account(request):
    """Delete user account"""
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        # Verify password
        if not request.user.check_password(password):
            messages.error(request, 'Password is incorrect.')
            return render(request, 'accounts/delete_account.html')
        
        # Proceed with account deletion
        confirm = request.POST.get('confirm', '')
        if confirm == 'DELETE':
            # Optional: Keep user data or archive it
            # For now, we'll soft-delete by marking as inactive
            user_email = request.user.email
            request.user.is_active = False
            request.user.save()
            
            # Log the user out
            logout(request)
            
            messages.success(request, f'Your account ({user_email}) has been deleted successfully. You have been logged out.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please type "DELETE" to confirm account deletion.')
            return render(request, 'accounts/delete_account.html')
    
    context = {}
    return render(request, 'accounts/delete_account.html', context)


@user_passes_test(lambda u: u.is_superuser)
def verify_kyc(request, pk):
    """Admin view to verify or reject uploaded KYC for a role upgrade request."""
    req = get_object_or_404(RoleUpgradeRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        if action == 'verify':
            req.verify_kyc(request.user, verified=True, notes=notes)
            messages.success(request, 'KYC marked as verified.')
            # Send HTML email
            ctx = {'user': req.user, 'request_obj': req}
            send_html_email('KYC Verified — Tick Entertainment', req.user.email, 'kyc_verified', ctx)
            # Audit + webhook
            audit_and_webhook(req, 'kyc_verified', admin_user=request.user, notes=notes)
        elif action == 'reject':
            req.verify_kyc(request.user, verified=False, notes=notes)
            messages.success(request, 'KYC marked as rejected.')
            ctx = {'user': req.user, 'request_obj': req, 'notes': notes}
            send_html_email('KYC Rejected — Tick Entertainment', req.user.email, 'kyc_rejected', ctx)
            audit_and_webhook(req, 'kyc_rejected', admin_user=request.user, notes=notes)
        return redirect('accounts:manage_role_requests')

    context = {
        'request_obj': req,
    }
    return render(request, 'accounts/verify_kyc.html', context)


@user_passes_test(lambda u: u.is_superuser)
def process_role_request(request, pk):
    """Admin approves or rejects a role upgrade request (KYC must be verified before approval)."""
    req = get_object_or_404(RoleUpgradeRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        if action == 'approve':
            try:
                req.approve(request.user)
                req.admin_notes = notes or req.admin_notes
                messages.success(request, 'Role upgrade request approved.')
                ctx = {'user': req.user, 'request_obj': req}
                send_html_email('Role Upgrade Approved — Tick Entertainment', req.user.email, 'role_approved', ctx)
                audit_and_webhook(req, 'role_approved', admin_user=request.user, notes=notes)
            except ValueError as e:
                messages.error(request, str(e))
        elif action == 'reject':
            req.reject(request.user, notes=notes)
            messages.success(request, 'Role upgrade request rejected.')
            ctx = {'user': req.user, 'request_obj': req, 'notes': notes}
            send_html_email('Role Upgrade Rejected — Tick Entertainment', req.user.email, 'role_rejected', ctx)
            audit_and_webhook(req, 'role_rejected', admin_user=request.user, notes=notes)
        return redirect('accounts:manage_role_requests')

    context = {'request_obj': req}
    return render(request, 'accounts/process_role_request.html', context)

