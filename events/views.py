from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
import json

from .models import Event, EventCategory, Booking, EventFavorite, EventShare
from .forms import EventForm, BookingForm

def event_list(request):
    """List all published events with filtering and search"""
    events = Event.objects.filter(status='published').order_by('start_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(venue_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).distinct()
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        events = events.filter(category__slug=category_slug)
    
    # Date filters
    date_filter = request.GET.get('date', '')
    if date_filter == 'today':
        events = events.filter(start_date__date=timezone.now().date())
    elif date_filter == 'week':
        events = events.filter(
            start_date__gte=timezone.now(),
            start_date__lte=timezone.now() + timezone.timedelta(days=7)
        )
    elif date_filter == 'month':
        events = events.filter(
            start_date__gte=timezone.now(),
            start_date__lte=timezone.now() + timezone.timedelta(days=30)
        )
    
    # Price filter
    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        events = events.filter(is_free=True)
    elif price_filter == 'paid':
        events = events.filter(is_free=False, ticket_price__gt=0)
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter sidebar
    categories = EventCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_date': date_filter,
        'selected_price': price_filter,
    }
    return render(request, 'events/event_list.html', context)

def event_list_by_category(request, category_slug):
    """List events by category"""
    category = get_object_or_404(EventCategory, slug=category_slug)
    events = Event.objects.filter(
        status='published',
        category=category
    ).order_by('start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
    }
    return render(request, 'events/event_list_by_category.html', context)

def upcoming_events(request):
    """List upcoming events"""
    events = Event.objects.filter(
        status='published',
        start_date__gt=timezone.now()
    ).order_by('start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Upcoming Events',
    }
    return render(request, 'events/event_list.html', context)

def past_events(request):
    """List past events"""
    events = Event.objects.filter(
        status='published',
        end_date__lt=timezone.now()
    ).order_by('-start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Past Events',
    }
    return render(request, 'events/event_list.html', context)

def featured_events(request):
    """List featured events"""
    events = Event.objects.filter(
        status='published',
        is_featured=True,
        start_date__gt=timezone.now()
    ).order_by('start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Featured Events',
    }
    return render(request, 'events/event_list.html', context)

def free_events(request):
    """List free events"""
    events = Event.objects.filter(
        status='published',
        is_free=True,
        start_date__gt=timezone.now()
    ).order_by('start_date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Free Events',
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, slug):
    """Event detail page"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    # Increment view count
    event.view_count += 1
    event.save(update_fields=['view_count'])
    
    # Check if user has favorited this event
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = EventFavorite.objects.filter(
            event=event,
            user=request.user
        ).exists()
    
    # Get related events
    related_events = Event.objects.filter(
        status='published',
        category=event.category,
        start_date__gt=timezone.now()
    ).exclude(id=event.id)[:6]
    
    # Get upcoming events by same host
    host_events = Event.objects.filter(
        status='published',
        host=event.host,
        start_date__gt=timezone.now()
    ).exclude(id=event.id)[:4]
    
    context = {
        'event': event,
        'is_favorited': is_favorited,
        'related_events': related_events,
        'host_events': host_events,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def book_event(request, slug):
    """Book tickets for an event"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    if event.is_sold_out:
        messages.error(request, 'This event is sold out!')
        return redirect('events:event_detail', slug=slug)
    
    if not event.is_upcoming:
        messages.error(request, 'This event has already passed!')
        return redirect('events:event_detail', slug=slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # Check availability
            if quantity > event.available_tickets_count:
                messages.error(request, f'Only {event.available_tickets_count} tickets available!')
                return redirect('events:event_detail', slug=slug)
            
            # Create booking (pending payment)
            booking = Booking.objects.create(
                event=event,
                user=request.user,
                quantity=quantity,
                unit_price=event.ticket_price,
                customer_name=request.user.get_full_name() or request.user.username,
                customer_email=request.user.email,
                customer_phone=request.user.phone_number or '',
            )
            
            # Redirect to payment page
            return redirect('payments:process_payment', booking_reference=booking.booking_reference)
    
    else:
        form = BookingForm()
    
    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'events/book_event.html', context)

@login_required
@require_POST
def favorite_event(request, slug):
    """Favorite/unfavorite an event"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    favorite, created = EventFavorite.objects.get_or_create(
        event=event,
        user=request.user
    )
    
    if not created:
        # Unfavorite
        favorite.delete()
        is_favorited = False
    else:
        # Favorite
        is_favorited = True
        # Update favorite count
        event.favorite_count += 1
        event.save(update_fields=['favorite_count'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'favorite_count': event.favorite_count,
        })
    
    messages.success(request, 'Event favorited!' if is_favorited else 'Event unfavorited!')
    return redirect('events:event_detail', slug=slug)

@login_required
def share_event(request, slug):
    """Track event sharing"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    if request.method == 'POST':
        platform = request.POST.get('platform')
        
        # Create share record
        EventShare.objects.create(
            event=event,
            user=request.user if request.user.is_authenticated else None,
            platform=platform,
            share_url=request.build_absolute_uri(event.get_absolute_url()),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update share count
        event.share_count += 1
        event.save(update_fields=['share_count'])
        
        # Redirect to share URL
        share_urls = {
            'whatsapp': f"https://wa.me/?text={event.title} - {request.build_absolute_uri(event.get_absolute_url())}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={request.build_absolute_uri(event.get_absolute_url())}",
            'twitter': f"https://twitter.com/intent/tweet?text={event.title}&url={request.build_absolute_uri(event.get_absolute_url())}",
            'email': f"mailto:?subject={event.title}&body=Check out this event: {request.build_absolute_uri(event.get_absolute_url())}",
        }
        
        return redirect(share_urls.get(platform, event.get_absolute_url()))
    
    return redirect('events:event_detail', slug=slug)

@login_required
def create_event(request):
    """Create a new event (for hosts)"""
    if not request.user.can_create_events():
        messages.error(request, 'You do not have permission to create events!')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_detail', slug=event.slug)
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': 'Create Event',
    }
    return render(request, 'events/create_event.html', context)

@login_required
def my_events(request):
    """List user's events (for hosts)"""
    if not request.user.can_create_events():
        messages.error(request, 'You do not have permission to manage events!')
        return redirect('core:home')
    
    events = Event.objects.filter(host=request.user).order_by('-created_at')
    
    context = {
        'events': events,
    }
    return render(request, 'events/my_events.html', context)

@login_required
def edit_event(request, pk):
    """Edit an event (for hosts)"""
    event = get_object_or_404(Event, pk=pk, host=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': 'Edit Event',
    }
    return render(request, 'events/edit_event.html', context)

@login_required
def delete_event(request, pk):
    """Delete an event (for hosts)"""
    event = get_object_or_404(Event, pk=pk, host=request.user)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:my_events')
    
    context = {
        'event': event,
    }
    return render(request, 'events/delete_event.html', context)

@login_required
def event_bookings(request, pk):
    """View event bookings (for hosts)"""
    event = get_object_or_404(Event, pk=pk, host=request.user)
    bookings = event.bookings.all().order_by('-booked_at')
    
    # Calculate statistics
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    total_revenue = bookings.filter(status='confirmed').aggregate(
        total=models.Sum('total_price')
    )['total'] or 0
    
    context = {
        'event': event,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
    }
    return render(request, 'events/event_bookings.html', context)

# AJAX views
@login_required
@require_POST
def ajax_book_event(request, event_id):
    """AJAX endpoint for booking events"""
    event = get_object_or_404(Event, id=event_id, status='published')
    
    if event.is_sold_out:
        return JsonResponse({'success': False, 'message': 'Event is sold out'})
    
    if not event.is_upcoming:
        return JsonResponse({'success': False, 'message': 'Event has already passed'})
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > event.available_tickets_count:
        return JsonResponse({
            'success': False, 
            'message': f'Only {event.available_tickets_count} tickets available'
        })
    
    # Create booking
    booking = Booking.objects.create(
        event=event,
        user=request.user,
        quantity=quantity,
        unit_price=event.ticket_price,
        customer_name=request.user.get_full_name() or request.user.username,
        customer_email=request.user.email,
        customer_phone=request.user.phone_number or '',
    )
    
    return JsonResponse({
        'success': True,
        'booking_reference': booking.booking_reference,
        'payment_url': reverse('payments:process_payment', kwargs={'booking_reference': booking.booking_reference}),
        'message': 'Booking created successfully'
    })

@login_required
@require_POST
def ajax_favorite_event(request, event_id):
    """AJAX endpoint for favoriting events"""
    event = get_object_or_404(Event, id=event_id, status='published')
    
    favorite, created = EventFavorite.objects.get_or_create(
        event=event,
        user=request.user
    )
    
    if not created:
        favorite.delete()
        is_favorited = False
        event.favorite_count = max(0, event.favorite_count - 1)
    else:
        is_favorited = True
        event.favorite_count += 1
    
    event.save(update_fields=['favorite_count'])
    
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'favorite_count': event.favorite_count,
    })

@login_required
@require_POST
def ajax_share_event(request, event_id):
    """AJAX endpoint for sharing events"""
    event = get_object_or_404(Event, id=event_id, status='published')
    platform = request.POST.get('platform')
    
    # Create share record
    EventShare.objects.create(
        event=event,
        user=request.user,
        platform=platform,
        share_url=request.build_absolute_uri(event.get_absolute_url()),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Update share count
    event.share_count += 1
    event.save(update_fields=['share_count'])
    
    return JsonResponse({
        'success': True,
        'share_count': event.share_count,
    })