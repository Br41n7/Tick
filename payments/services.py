import requests
from django.conf import settings
from django.utils import timezone

class PaystackService:
    """Service class for interacting with Paystack API"""
    
    BASE_URL = 'https://api.paystack.co'
    
    def __init__(self):
        self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        self.public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        self.test_mode = getattr(settings, 'PAYSTACK_TEST_MODE', True)
    
    def get_headers(self):
        """Get request headers with authorization"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def initialize_transaction(self, payment_data):
        """Initialize a Paystack transaction"""
        url = f'{self.BASE_URL}/transaction/initialize'
        
        try:
            response = requests.post(url, json=payment_data, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def verify_transaction(self, reference):
        """Verify a Paystack transaction"""
        url = f'{self.BASE_URL}/transaction/verify/{reference}'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def transfer_recipient(self, recipient_data):
        """Create a transfer recipient"""
        url = f'{self.BASE_URL}/transferrecipient'
        
        try:
            response = requests.post(url, json=recipient_data, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def initiate_transfer(self, transfer_data):
        """Initiate a transfer"""
        url = f'{self.BASE_URL}/transfer'
        
        try:
            response = requests.post(url, json=transfer_data, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def verify_transfer(self, transfer_code):
        """Verify a transfer"""
        url = f'{self.BASE_URL}/transfer/verify/{transfer_code}'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def get_transaction(self, transaction_id):
        """Get transaction details"""
        url = f'{self.BASE_URL}/transaction/{transaction_id}'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def list_transactions(self, params=None):
        """List transactions"""
        url = f'{self.BASE_URL}/transaction'
        
        try:
            response = requests.get(url, params=params, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def get_balance(self):
        """Get account balance"""
        url = f'{self.BASE_URL}/balance'
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': False, 'message': str(e)}
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature"""
        # You need to implement this based on Paystack's webhook verification
        # This is a placeholder implementation
        return True