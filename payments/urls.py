from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment processing
    path('process/<str:booking_reference>/', views.process_payment, name='process_payment'),
    path('success/<str:booking_reference>/', views.payment_success, name='payment_success'),
    path('failed/<str:booking_reference>/', views.payment_failed, name='payment_failed'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
    
    # Transaction history
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transaction/<str:reference>/', views.transaction_detail, name='transaction_detail'),
    
    # Host earnings and payouts (for hosts)
    path('earnings/', views.host_earnings, name='host_earnings'),
    path('payouts/', views.payout_history, name='payout_history'),
    # path('request-payout/', views.request_payout, name='request_payout'),
]