from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [ path('create/', views.create_event, name='create_event'),
    # Event listing and filtering
    path('', views.event_list, name='event_list'),
    path('my-events/', views.my_events, name='my_events'),
    path('category/<slug:category_slug>/', views.event_list_by_category, name='event_list_by_category'),
    path('upcoming/', views.upcoming_events, name='upcoming_events'),
    path('past/', views.past_events, name='past_events'),
    path('featured/', views.featured_events, name='featured_events'),
    path('free/', views.free_events, name='free_events'),
    
    # Event details and actions
    path('<slug:slug>/', views.event_detail, name='event_detail'),
    path('<slug:slug>/book/', views.book_event, name='book_event'),
    path('<slug:slug>/favorite/', views.favorite_event, name='favorite_event'),
    path('<slug:slug>/share/', views.share_event, name='share_event'),
    
    # Host event management
    path('<int:event_id>/', views.event_detail, name='event-detail'),
    path('edit/<int:pk>/', views.edit_event, name='edit_event'),
    path('delete/<int:pk>/', views.delete_event, name='delete_event'),
    path('<int:pk>/bookings/', views.event_bookings, name='event_bookings'),
    
    # AJAX endpoints
    path('ajax/book/<int:event_id>/', views.ajax_book_event, name='ajax_book_event'),
    path('ajax/track_action/', views.ajax_track_action, name='ajax_track_action'),
    path('ajax/favorite/<int:event_id>/', views.ajax_favorite_event, name='ajax_favorite_event'),
    path('ajax/share/<int:event_id>/', views.ajax_share_event, name='ajax_share_event'),
]