import json
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal

from events.models import Booking
from .models import Transaction, Commission, Payout
from .services import PaystackService

def process_payment(request, booking_reference):
    """Process payment for a booking"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)
    
    if booking.status != 'pending':
        messages.error(request, 'This booking has already been processed!')
        return redirect('events:my_bookings')
    
    # Get Paystack service
    paystack_service = PaystackService()
    
    # Initialize payment
    payment_data = {
        'email': booking.customer_email,
        'amount': int(booking.total_price * 100),  # Convert to kobo/cents
        'reference': booking.booking_reference,
        'callback_url': request.build_absolute_uri(
            reverse('payments:payment_success', kwargs={'booking_reference': booking.booking_reference})
        ),
        'metadata': {
            'booking_reference': booking.booking_reference,
            'user_id': request.user.id,
            'event_id': booking.event.id,
            'quantity': booking.quantity
        }
    }
    
    try:
        response = paystack_service.initialize_transaction(payment_data)
        
        if response['status']:
            # Create transaction record
            transaction = Transaction.objects.create(
                reference=booking.booking_reference,
                transaction_type='booking',
                user=request.user,
                amount=booking.total_price,
                payment_method='paystack',
                paystack_reference=response['data']['reference'],
                description=f"Payment for {booking.quantity} ticket(s) to {booking.event.title}",
                booking=booking
            )
            
            # Redirect to Paystack payment page
            return redirect(response['data']['authorization_url'])
        else:
            messages.error(request, 'Payment initialization failed. Please try again.')
            return redirect('events:event_detail', slug=booking.event.slug)
            
    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('events:event_detail', slug=booking.event.slug)

def payment_success(request, booking_reference):
    """Handle successful payment callback"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)
    
    # Verify payment with Paystack
    paystack_service = PaystackService()
    
    try:
        # Get transaction reference from URL parameter
        trxref = request.GET.get('trxref') or request.GET.get('reference')
        
        if trxref:
            # Verify transaction
            response = paystack_service.verify_transaction(trxref)
            
            if response['status'] and response['data']['status'] == 'success':
                # Update booking status
                booking.status = 'confirmed'
                booking.payment_reference = trxref
                booking.save()
                
                # Update transaction
                transaction = Transaction.objects.get(reference=booking_reference)
                transaction.status = 'success'
                transaction.gateway_response = response['data']
                transaction.processed_at = timezone.now()
                transaction.save()
                
                # Create commission record
                commission = Commission.objects.create(
                    transaction=transaction,
                    booking=booking,
                    event=booking.event,
                    host=booking.event.host,
                    booking_amount=booking.total_price,
                    commission_rate=Decimal('10.00'),  # 10% commission
                )
                
                # Update event sold tickets
                booking.event.sold_tickets += booking.quantity
                booking.event.save(update_fields=['sold_tickets'])
                
                messages.success(request, 'Payment successful! Your booking is confirmed.')
                return redirect('payments:transaction_detail', reference=booking_reference)
            else:
                # Payment verification failed
                transaction = Transaction.objects.get(reference=booking_reference)
                transaction.status = 'failed'
                transaction.gateway_response = response.get('data', {})
                transaction.save()
                
                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect('payments:payment_failed', booking_reference=booking_reference)
        else:
            messages.error(request, 'Payment reference not found.')
            return redirect('payments:payment_failed', booking_reference=booking_reference)
            
    except Exception as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('payments:payment_failed', booking_reference=booking_reference)

def payment_failed(request, booking_reference):
    """Handle failed payment"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)
    
    context = {
        'booking': booking,
        'booking_reference': booking_reference,
    }
    return render(request, 'payments/payment_failed.html', context)

@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhooks"""
    try:
        # Get the raw body and verify signature
        payload = request.body
        signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        
        # Verify webhook signature (you should implement this)
        # For now, we'll process the webhook
        
        data = json.loads(payload)
        event_type = data.get('event')
        
        if event_type == 'charge.success':
            # Process successful payment
            reference = data['data']['reference']
            transaction = Transaction.objects.filter(paystack_reference=reference).first()
            
            if transaction:
                transaction.status = 'success'
                transaction.gateway_response = data['data']
                transaction.processed_at = timezone.now()
                transaction.save()
                
                # Update booking
                if transaction.booking:
                    transaction.booking.status = 'confirmed'
                    transaction.booking.payment_reference = reference
                    transaction.booking.save()
        
        elif event_type == 'charge.failed':
            # Process failed payment
            reference = data['data']['reference']
            transaction = Transaction.objects.filter(paystack_reference=reference).first()
            
            if transaction:
                transaction.status = 'failed'
                transaction.gateway_response = data['data']
                transaction.save()
        
        return HttpResponse(status=200)
        
    except Exception as e:
        return HttpResponse(status=400)

@login_required
def transaction_history(request):
    """View user's transaction history"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Filter by transaction type
    type_filter = request.GET.get('type', '')
    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)
    
    context = {
        'transactions': transactions,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'payments/transaction_history.html', context)

@login_required
def transaction_detail(request, reference):
    """View transaction details"""
    transaction = get_object_or_404(Transaction, reference=reference, user=request.user)
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/transaction_detail.html', context)

@login_required
def host_earnings(request):
    """View host earnings dashboard"""
    if not request.user.can_create_events():
        messages.error(request, 'You do not have permission to view earnings!')
        return redirect('core:home')
    
    # Get commissions for user's events
    commissions = Commission.objects.filter(host=request.user).order_by('-created_at')
    
    # Calculate totals
    total_earnings = commissions.filter(status='calculated').aggregate(
        total=models.Sum('host_earnings')
    )['total'] or Decimal('0.00')
    
    total_commission = commissions.filter(status='calculated').aggregate(
        total=models.Sum('commission_amount')
    )['total'] or Decimal('0.00')
    
    pending_earnings = commissions.filter(status='pending').aggregate(
        total=models.Sum('host_earnings')
    )['total'] or Decimal('0.00')
    
    context = {
        'commissions': commissions,
        'total_earnings': total_earnings,
        'total_commission': total_commission,
        'pending_earnings': pending_earnings,
    }
    return render(request, 'payments/host_earnings.html', context)

@login_required
def payout_history(request):
    """View payout history"""
    payouts = Payout.objects.filter(host=request.user).order_by('-created_at')
    
    context = {
        'payouts': payouts,
    }
    return render(request, 'payments/payout_history.html', context)