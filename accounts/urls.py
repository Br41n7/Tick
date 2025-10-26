from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User profile
    path('profile/', views.user_profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Dashboard (redirects to appropriate dashboard based on role)
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # My bookings
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<str:reference>/', views.booking_detail, name='booking_detail'),
    
    # Favorites and following
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('following/', views.my_following, name='my_following'),
    
    # Role upgrade requests
    path('upgrade-request/', views.request_role_upgrade, name='request_role_upgrade'),
    path('upgrade-requests/', views.my_upgrade_requests, name='my_upgrade_requests'),
    
    # Host dashboard
    path('host/dashboard/', views.host_dashboard, name='host_dashboard'),
    path('host/events/', views.my_events, name='my_events'),
    # path('host/analytics/', views.host_analytics, name='host_analytics'),
    
    # Artist dashboard
    path('artist/dashboard/', views.artist_dashboard, name='artist_dashboard'),
    # path('artist/profile/', views.artist_profile_edit, name='artist_profile_edit'),
    # path('artist/reels/', views.my_reels, name='my_reels'),
    # path('artist/stats/', views.artist_stats, name='artist_stats'),
    
    # Admin dashboard
    # path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin/users/', views.manage_users, name='manage_users'),
    # path('admin/role-requests/', views.manage_role_requests, name='manage_role_requests'),
    # path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
]