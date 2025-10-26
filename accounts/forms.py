from django import forms
from django.contrib.auth import get_user_model
from .models import RoleUpgradeRequest

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'avatar', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RoleUpgradeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleUpgradeRequest
        fields = ['request_type', 'reason']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter available upgrade options based on current user roles
            choices = [('', 'Select upgrade type...')]
            
            if not user.is_artist:
                choices.append(('to_artist', 'Upgrade to Artist'))
            if not user.is_host:
                choices.append(('to_host', 'Upgrade to Host'))
            
            self.fields['request_type'].choices = choices