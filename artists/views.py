from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
import json

from .models import ArtistProfile, Reel, ReelView, ReelLike, Follow
from .forms import ArtistProfileForm, ReelForm
from events.models import Event

def artist_list(request):
    """List all artists with filtering and search"""
    artists = ArtistProfile.objects.all().order_by('-follower_count')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        artists = artists.filter(
            Q(stage_name__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(genre__icontains=search_query)
        ).distinct()
    
    # Genre filter
    genre = request.GET.get('genre', '')
    if genre:
        artists = artists.filter(genre__icontains=genre)
    
    # Sort options
    sort = request.GET.get('sort', 'followers')
    if sort == 'followers':
        artists = artists.order_by('-follower_count')
    elif sort == 'reels':
        artists = artists.annotate(reel_count=Count('reels')).order_by('-reel_count')
    elif sort == 'views':
        artists = artists.order_by('-total_views')
    elif sort == 'newest':
        artists = artists.order_by('-created_at')
    elif sort == 'verified':
        artists = artists.filter(is_verified=True).order_by('-follower_count')
    
    # Pagination
    paginator = Paginator(artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique genres for filter
    genres = ArtistProfile.objects.values_list('genre', flat=True).distinct()
    genres = [g for g in genres if g]  # Remove empty values
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_genre': genre,
        'selected_sort': sort,
        'genres': genres,
    }
    return render(request, 'artists/artist_list.html', context)

def artist_list_by_genre(request, genre):
    """List artists by genre"""
    artists = ArtistProfile.objects.filter(genre__icontains=genre).order_by('-follower_count')
    
    paginator = Paginator(artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genre': genre,
    }
    return render(request, 'artists/artist_list_by_genre.html', context)

def featured_artists(request):
    """List featured artists"""
    artists = ArtistProfile.objects.filter(is_featured=True).order_by('-follower_count')
    
    paginator = Paginator(artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Featured Artists',
    }
    return render(request, 'artists/artist_list.html', context)

def trending_artists(request):
    """List trending artists (by recent activity)"""
    # Trending based on recent views and follows
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    
    trending_ids = []
    for artist in ArtistProfile.objects.all():
        recent_views = ReelView.objects.filter(
            reel__artist=artist,
            viewed_at__gte=one_week_ago
        ).count()
        
        recent_follows = Follow.objects.filter(
            artist=artist,
            created_at__gte=one_week_ago
        ).count()
        
        # Simple trending score
        score = recent_views * 1 + recent_follows * 10
        trending_ids.append((artist.id, score))
    
    # Sort by score and get top artists
    trending_ids.sort(key=lambda x: x[1], reverse=True)
    trending_ids = [tid for tid, score in trending_ids[:50]]
    
    artists = ArtistProfile.objects.filter(id__in=trending_ids)
    
    # Maintain order
    ordered_artists = []
    for tid in trending_ids:
        for artist in artists:
            if artist.id == tid:
                ordered_artists.append(artist)
                break
    
    paginator = Paginator(ordered_artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Trending Artists',
    }
    return render(request, 'artists/artist_list.html', context)

def artist_detail(request, slug):
    """Artist profile page"""
    artist = get_object_or_404(ArtistProfile, slug=slug)
    
    # Check if user follows this artist
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            artist=artist,
            follower=request.user
        ).exists()
    
    # Get artist's reels
    reels = artist.reels.filter(status='published').order_by('-created_at')
    
    # Get artist's upcoming events
    events = Event.objects.filter(
        host=artist.user,
        status='published',
        start_date__gt=timezone.now()
    ).order_by('start_date')
    
    # Get similar artists
    similar_artists = ArtistProfile.objects.filter(
        genre__icontains=artist.genre
    ).exclude(id=artist.id).order_by('-follower_count')[:6]
    
    context = {
        'artist': artist,
        'is_following': is_following,
        'reels': reels[:6],  # Show first 6 reels
        'events': events[:3],  # Show first 3 events
        'similar_artists': similar_artists,
        'total_reels': reels.count(),
    }
    return render(request, 'artists/artist_detail.html', context)

@login_required
@require_POST
def follow_artist(request, slug):
    """Follow/unfollow an artist"""
    artist = get_object_or_404(ArtistProfile, slug=slug)
    
    follow, created = Follow.objects.get_or_create(
        artist=artist,
        follower=request.user
    )
    
    if not created:
        # Unfollow
        follow.delete()
        is_following = False
        artist.follower_count = max(0, artist.follower_count - 1)
    else:
        # Follow
        is_following = True
        artist.follower_count += 1
    
    artist.save(update_fields=['follower_count'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_following': is_following,
            'follower_count': artist.follower_count,
        })
    
    messages.success(request, 'Following artist!' if is_following else 'Unfollowed artist!')
    return redirect('artists:artist_detail', slug=slug)

def artist_followers(request, slug):
    """List artist's followers"""
    artist = get_object_or_404(ArtistProfile, slug=slug)
    followers = Follow.objects.filter(artist=artist).order_by('-created_at')
    
    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artist': artist,
        'page_obj': page_obj,
    }
    return render(request, 'artists/artist_followers.html', context)

def artist_reels(request, slug):
    """List artist's reels"""
    artist = get_object_or_404(ArtistProfile, slug=slug)
    reels = artist.reels.filter(status='published').order_by('-created_at')
    
    paginator = Paginator(reels, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artist': artist,
        'page_obj': page_obj,
    }
    return render(request, 'artists/artist_reels.html', context)

def reel_detail(request, slug):
    """Reel detail page"""
    reel = get_object_or_404(Reel, slug=slug, status='published')
    
    # Track view
    if request.user.is_authenticated:
        ReelView.objects.get_or_create(
            reel=reel,
            user=request.user,
            defaults={
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
    else:
        # Track anonymous views (less frequently)
        import uuid
        session_key = request.session.session_key or str(uuid.uuid4())
        if not hasattr(request, '_reel_views_tracked'):
            request._reel_views_tracked = set()
        
        if reel.id not in request._reel_views_tracked:
            ReelView.objects.get_or_create(
                reel=reel,
                user=None,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            request._reel_views_tracked.add(reel.id)
    
    # Update view count (update less frequently)
    if request.user.is_authenticated:
        new_count = ReelView.objects.filter(reel=reel).count()
        if new_count > reel.view_count:
            reel.view_count = new_count
            reel.save(update_fields=['view_count'])
    
    # Check if user liked this reel
    is_liked = False
    if request.user.is_authenticated:
        is_liked = ReelLike.objects.filter(
            reel=reel,
            user=request.user
        ).exists()
    
    # Get related reels
    related_reels = Reel.objects.filter(
        artist=reel.artist,
        status='published'
    ).exclude(id=reel.id).order_by('-created_at')[:6]
    
    context = {
        'reel': reel,
        'is_liked': is_liked,
        'related_reels': related_reels,
    }
    return render(request, 'artists/reel_detail.html', context)

@login_required
@require_POST
def like_reel(request, slug):
    """Like/unlike a reel"""
    reel = get_object_or_404(Reel, slug=slug, status='published')
    
    like, created = ReelLike.objects.get_or_create(
        reel=reel,
        user=request.user
    )
    
    if not created:
        # Unlike
        like.delete()
        is_liked = False
        reel.like_count = max(0, reel.like_count - 1)
    else:
        # Like
        is_liked = True
        reel.like_count += 1
    
    reel.save(update_fields=['like_count'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'like_count': reel.like_count,
        })
    
    messages.success(request, 'Liked reel!' if is_liked else 'Unliked reel!')
    return redirect('artists:reel_detail', slug=slug)

@login_required
def share_reel(request, slug):
    """Share a reel"""
    reel = get_object_or_404(Reel, slug=slug, status='published')
    
    if request.method == 'POST':
        platform = request.POST.get('platform')
        
        # Track share (similar to event sharing)
        # Add sharing logic here if needed
        
        # Redirect to share URL
        share_urls = {
            'whatsapp': f"https://wa.me/?text={reel.title} - {request.build_absolute_uri(reel.get_absolute_url())}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={request.build_absolute_uri(reel.get_absolute_url())}",
            'twitter': f"https://twitter.com/intent/tweet?text={reel.title}&url={request.build_absolute_uri(reel.get_absolute_url())}",
            'email': f"mailto:?subject={reel.title}&body=Check out this reel: {request.build_absolute_uri(reel.get_absolute_url())}",
        }
        
        return redirect(share_urls.get(platform, reel.get_absolute_url()))
    
    return redirect('artists:reel_detail', slug=slug)

@login_required
def artist_dashboard(request):
    """Artist dashboard"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to access artist dashboard!')
        return redirect('core:home')
    
    try:
        artist_profile = request.user.artist_profile
    except ArtistProfile.DoesNotExist:
        messages.error(request, 'Please complete your artist profile first!')
        return redirect('artists:edit_artist_profile')
    
    # Get statistics
    total_views = artist_profile.reels.aggregate(total=Sum('view_count'))['total'] or 0
    total_likes = artist_profile.reels.aggregate(total=Sum('like_count'))['total'] or 0
    recent_reels = artist_profile.reels.all().order_by('-created_at')[:5]
    recent_followers = artist_profile.followers.all().order_by('-created_at')[:5]
    
    context = {
        'artist_profile': artist_profile,
        'total_views': total_views,
        'total_likes': total_likes,
        'recent_reels': recent_reels,
        'recent_followers': recent_followers,
    }
    return render(request, 'artists/artist_dashboard.html', context)

@login_required
def edit_artist_profile(request):
    """Edit artist profile"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to edit artist profile!')
        return redirect('core:home')
    
    try:
        artist_profile = request.user.artist_profile
    except ArtistProfile.DoesNotExist:
        artist_profile = ArtistProfile(user=request.user)
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artist profile updated successfully!')
            return redirect('artists:artist_dashboard')
    else:
        # Prefill sensible defaults from the user's account when creating a new profile
        if not artist_profile.pk:
            full_name = (request.user.get_full_name() or request.user.username or '')
            default_stage = full_name.strip() if full_name.strip() else request.user.username
            initial = {
                'stage_name': default_stage,
                'booking_email': request.user.email,
                'phone_number': getattr(request.user, 'phone_number', '') or ''
            }
            form = ArtistProfileForm(instance=artist_profile, initial=initial)
        else:
            form = ArtistProfileForm(instance=artist_profile)
    
    context = {
        'form': form,
        'title': 'Edit Artist Profile',
        'artist_profile': artist_profile,
    }
    return render(request, 'artists/edit_artist_profile.html', context)

@login_required
def upload_reel(request):
    """Upload a new reel"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to upload reels!')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.artist = request.user.artist_profile
            reel.save()
            
            messages.success(request, 'Reel uploaded successfully!')
            return redirect('artists:manage_reels')
    else:
        form = ReelForm()
    
    context = {
        'form': form,
        'title': 'Upload Reel',
    }
    return render(request, 'artists/upload_reel.html', context)

@login_required
def manage_reels(request):
    """Manage artist's reels"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to manage reels!')
        return redirect('core:home')
    
    reels = request.user.artist_profile.reels.all().order_by('-created_at')
    
    context = {
        'reels': reels,
    }
    return render(request, 'artists/manage_reels.html', context)

@login_required
def edit_reel(request, pk):
    """Edit a reel"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to edit reels!')
        return redirect('core:home')
    
    reel = get_object_or_404(Reel, pk=pk, artist=request.user.artist_profile)
    
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES, instance=reel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reel updated successfully!')
            return redirect('artists:manage_reels')
    else:
        form = ReelForm(instance=reel)
    
    context = {
        'form': form,
        'reel': reel,
        'title': 'Edit Reel',
    }
    return render(request, 'artists/edit_reel.html', context)

@login_required
def delete_reel(request, pk):
    """Delete a reel"""
    if not request.user.can_upload_reels():
        messages.error(request, 'You do not have permission to delete reels!')
        return redirect('core:home')
    
    reel = get_object_or_404(Reel, pk=pk, artist=request.user.artist_profile)
    
    if request.method == 'POST':
        reel.delete()
        messages.success(request, 'Reel deleted successfully!')
        return redirect('artists:manage_reels')
    
    context = {
        'reel': reel,
    }
    return render(request, 'artists/delete_reel.html', context)

# AJAX views
@login_required
@require_POST
def ajax_follow_artist(request, artist_id):
    """AJAX endpoint for following artists"""
    artist = get_object_or_404(ArtistProfile, id=artist_id)
    
    follow, created = Follow.objects.get_or_create(
        artist=artist,
        follower=request.user
    )
    
    if not created:
        follow.delete()
        is_following = False
        artist.follower_count = max(0, artist.follower_count - 1)
    else:
        is_following = True
        artist.follower_count += 1
    
    artist.save(update_fields=['follower_count'])
    
    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'follower_count': artist.follower_count,
    })

@login_required
@require_POST
def ajax_like_reel(request, reel_id):
    """AJAX endpoint for liking reels"""
    reel = get_object_or_404(Reel, id=reel_id, status='published')
    
    like, created = ReelLike.objects.get_or_create(
        reel=reel,
        user=request.user
    )
    
    if not created:
        like.delete()
        is_liked = False
        reel.like_count = max(0, reel.like_count - 1)
    else:
        is_liked = True
        reel.like_count += 1
    
    reel.save(update_fields=['like_count'])
    
    return JsonResponse({
        'success': True,
        'is_liked': is_liked,
        'like_count': reel.like_count,
    })

def ajax_view_reel(request, reel_id):
    """AJAX endpoint for tracking reel views"""
    reel = get_object_or_404(Reel, id=reel_id, status='published')
    
    # Track view
    ReelView.objects.create(
        reel=reel,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    # Increment the aggregate view count (best-effort)
    reel.view_count = F('view_count') + 1
    reel.save(update_fields=['view_count'])
    # Refresh from DB to get the actual integer value
    reel.refresh_from_db()

    return JsonResponse({
        'success': True,
        'view_count': reel.view_count,
    })
    
    