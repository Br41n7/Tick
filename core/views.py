from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from events.models import Event
from artists.models import ArtistProfile, Reel
from .models import FAQ, ContactMessage, SiteConfiguration

def home(request):
    """Home page with featured events and artists"""
    featured_events = Event.objects.filter(
        status='published',
        is_featured=True,
        is_upcoming=True
    ).order_by('-start_date')[:6]
    
    featured_artists = ArtistProfile.objects.filter(
        is_featured=True
    ).order_by('-follower_count')[:6]
    
    popular_reels = Reel.objects.filter(
        status='published'
    ).order_by('-view_count')[:8]
    
    context = {
        'featured_events': featured_events,
        'featured_artists': featured_artists,
        'popular_reels': popular_reels,
    }
    return render(request, 'core/home.html', context)

def about(request):
    """About page"""
    return render(request, 'core/about.html')

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Get user IP and user agent
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')

def faq(request):
    """FAQ page"""
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    categories = FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    
    context = {
        'faqs': faqs,
        'categories': categories,
    }
    return render(request, 'core/faq.html', context)

def search(request):
    """Global search functionality"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    events = []
    artists = []
    reels = []
    
    if query:
        if search_type in ['all', 'events']:
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(venue_name__icontains=query) |
                Q(category__name__icontains=query)
            ).filter(status='published').distinct()
        
        if search_type in ['all', 'artists']:
            artists = ArtistProfile.objects.filter(
                Q(stage_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(genre__icontains=query)
            ).distinct()
        
        if search_type in ['all', 'reels']:
            reels = Reel.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(artist__stage_name__icontains=query)
            ).filter(status='published').distinct()
    
    context = {
        'query': query,
        'search_type': search_type,
        'events': events,
        'artists': artists,
        'reels': reels,
        'total_results': len(events) + len(artists) + len(reels),
    }
    return render(request, 'core/search.html', context)

@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    
    # Get user's recent activities
    recent_bookings = user.bookings.all().order_by('-booked_at')[:5]
    favorite_events = user.favorite_events.all().order_by('-created_at')[:5]
    following_artists = user.following_artists.all().order_by('-created_at')[:5]
    
    # If user is host, get their events
    user_events = []
    if user.can_create_events():
        user_events = user.hosted_events.filter(status__in=['published', 'draft']).order_by('-created_at')[:5]
    
    # If user is artist, get their reels
    user_reels = []
    if user.can_upload_reels():
        artist_profile = getattr(user, 'artist_profile', None)
        if artist_profile:
            user_reels = artist_profile.reels.filter(status='published').order_by('-created_at')[:5]
    
    context = {
        'recent_bookings': recent_bookings,
        'favorite_events': favorite_events,
        'following_artists': following_artists,
        'user_events': user_events,
        'user_reels': user_reels,
    }
    return render(request, 'core/dashboard.html', context)