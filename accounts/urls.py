from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('profile/', views.user_profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Account management
    path('upgrade-role/', views.upgrade_role, name='upgrade_role'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # Dashboard (redirects to appropriate dashboard based on role)
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
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
    
    # Artist dashboard
    path('artist/dashboard/', views.artist_dashboard, name='artist_dashboard'),
    
    # Admin dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('admin/role-requests/', views.manage_role_requests, name='manage_role_requests'),
    path('admin/role-requests/<int:pk>/verify-kyc/', views.verify_kyc, name='verify_kyc'),
    path('admin/role-requests/<int:pk>/process/', views.process_role_request, name='process_role_request'),
#    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
]