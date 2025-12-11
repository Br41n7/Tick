from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    # Artist listing and discovery
     path('', views.artist_list, name='artist_list'),
     path('upload-reel/', views.upload_reel, name='upload_reel'),
     path('genre/<slug:genre>/', views.artist_list_by_genre, name='artist_list_by_genre'),
     path('featured/', views.featured_artists, name='featured_artists'),
     path('trending/', views.trending_artists, name='trending_artists'),
    
    # Artist dashboard and management (static paths first so they are not captured by slug routes)
     path('dashboard/', views.artist_dashboard, name='artist_dashboard'),
     path('profile/', views.edit_artist_profile, name='edit_artist_profile'),

    path('reels/', views.manage_reels, name='manage_reels'),
    path('edit-reel/<int:pk>/', views.edit_reel, name='edit_reel'),
    path('delete-reel/<int:pk>/', views.delete_reel, name='delete_reel'),

    # Backwards-compatible alias used in templates: `artists:my_reels`
    path('my-reels/', views.manage_reels, name='my_reels'),

    # Reel detail and actions
     path('reel/<slug:slug>/', views.reel_detail, name='reel_detail'),
     path('reel/<slug:slug>/like/', views.like_reel, name='like_reel'),
     path('reel/<slug:slug>/share/', views.share_reel, name='share_reel'),

    # AJAX endpoints
     path('ajax/follow/<int:artist_id>/', views.ajax_follow_artist, name='ajax_follow_artist'),
     path('ajax/like/<int:reel_id>/', views.ajax_like_reel, name='ajax_like_reel'),
     path('ajax/view/<int:reel_id>/', views.ajax_view_reel, name='ajax_view_reel'),

    # Artist profile and slug-based routes (placed last to avoid catching static paths like 'profile')
     path('<slug:slug>/follow/', views.follow_artist, name='follow_artist'),
     path('<slug:slug>/followers/', views.artist_followers, name='artist_followers'),
     path('<slug:slug>/reels/', views.artist_reels, name='artist_reels'),
     path('<slug:slug>/', views.artist_detail, name='artist_detail'),
]