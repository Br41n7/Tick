from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import RoleUpgradeRequest
from .forms import UserProfileForm, RoleUpgradeRequestForm
from events.models import Event, Booking, EventFavorite
from artists.models import ArtistProfile, Reel, Follow
from payments.models import Transaction, Commission

User = get_user_model()

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
        
        context = {
            'recent_bookings': recent_bookings,
            'favorite_events': favorite_events,
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
        form = RoleUpgradeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            upgrade_request = form.save(commit=False)
            upgrade_request.user = request.user
            upgrade_request.save()
            
            messages.success(request, 'Role upgrade request submitted successfully!')
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