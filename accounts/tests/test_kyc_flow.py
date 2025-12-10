from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import RoleUpgradeRequest, KycAuditLog
from unittest.mock import patch

User = get_user_model()

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class KycFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='pass')
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')

    def test_user_submits_kyc_and_admin_verifies_and_approves(self):
        # user uploads a KYC doc via model directly
        f = SimpleUploadedFile('id.png', b'filecontent', content_type='image/png')
        req = RoleUpgradeRequest.objects.create(user=self.user, request_type='to_artist', reason='I want to create reels', kyc_document=f)
        self.assertEqual(req.kyc_status, 'pending')

        # Admin verifies KYC
        self.client.login(email='admin@example.com', password='adminpass')
        url = reverse('accounts:verify_kyc', args=[req.pk])
        resp = self.client.post(url, {'action': 'verify', 'notes': 'Looks good'})
        req.refresh_from_db()
        self.assertEqual(req.kyc_status, 'verified')
        # audit log created
        self.assertTrue(KycAuditLog.objects.filter(request=req, action='kyc_verified').exists())

        # Now approve the role request
        url2 = reverse('accounts:process_role_request', args=[req.pk])
        resp2 = self.client.post(url2, {'action': 'approve', 'notes': 'Approved'})
        req.refresh_from_db()
        self.assertEqual(req.status, 'approved')
        # role upgraded on user
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_artist or self.user.role == 'artist')

    @patch('accounts.utils.requests')
    def test_webhook_called_on_audit(self, mock_requests):
        f = SimpleUploadedFile('id2.png', b'filecontent', content_type='image/png')
        req = RoleUpgradeRequest.objects.create(user=self.user, request_type='to_host', reason='I host events', kyc_document=f)
        mock_requests.post.return_value.status_code = 200
        self.client.login(email='admin@example.com', password='adminpass')
        url = reverse('accounts:verify_kyc', args=[req.pk])
        with patch('django.conf.settings.KYC_WEBHOOK_URL', new='http://example.com/webhook'):
            resp = self.client.post(url, {'action': 'verify', 'notes': 'OK'})
            # requests.post called
            self.assertTrue(mock_requests.post.called)