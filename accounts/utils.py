from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import json

try:
    import requests
except Exception:
    requests = None

from .models import KycAuditLog


def send_html_email(subject, to_email, template_base, context=None):
    """Send HTML + plain-text email using EmailMultiAlternatives.

    template_base is the base name for templates under templates/emails/,
    e.g. 'kyc_verified' -> 'emails/kyc_verified.html' and '.txt'.
    """
    context = context or {}
    text_body = render_to_string(f'emails/{template_base}.txt', context)
    html_body = render_to_string(f'emails/{template_base}.html', context)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'no-reply@example.com')
    msg = EmailMultiAlternatives(subject=subject, body=text_body, from_email=from_email, to=[to_email])
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send(fail_silently=True)
    except Exception:
        # don't crash the caller on email failures
        pass


def post_webhook(url, payload):
    if not url or not requests:
        return None
    try:
        resp = requests.post(url, json=payload, timeout=5)
        return resp
    except Exception:
        return None


def audit_and_webhook(request_obj, action, admin_user=None, notes=''):
    """Create an audit log and post to configured webhook if present.

    action: e.g. 'kyc_verified', 'kyc_rejected', 'role_approved', 'role_rejected'
    """
    # Create audit log
    log = KycAuditLog.objects.create(
        request=request_obj,
        action=action,
        admin=admin_user,
        notes=notes,
    )

    # Fire webhook if configured
    webhook_url = getattr(settings, 'KYC_WEBHOOK_URL', None)
    if webhook_url:
        payload = {
            'request_id': request_obj.pk,
            'user_email': request_obj.user.email,
            'action': action,
            'notes': notes,
            'timestamp': str(log.created_at),
        }
        post_webhook(webhook_url, payload)

    return log
