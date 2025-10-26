from django import forms
from django.utils import timezone
from .models import Event, EventCategory, Booking

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'category',
            'venue_name', 'venue_address', 'city', 'state', 'country',
            'start_date', 'end_date', 'ticket_price', 'available_tickets',
            'image', 'featured_image', 'is_featured', 'is_free'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'venue_name': forms.TextInput(attrs={'class': 'form-control'}),
            'venue_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'available_tickets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date and start_date < timezone.now():
            raise forms.ValidationError("Start date cannot be in the past!")
        return start_date

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data['end_date']
        
        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date!")
        return end_date

    def clean_available_tickets(self):
        available_tickets = self.cleaned_data['available_tickets']
        if available_tickets and available_tickets < 1:
            raise forms.ValidationError("Available tickets must be at least 1!")
        return available_tickets

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        ticket_price = cleaned_data.get('ticket_price')
        
        if is_free and ticket_price and ticket_price > 0:
            raise forms.ValidationError("Free events cannot have a ticket price!")
        
        if not is_free and not ticket_price:
            raise forms.ValidationError("Paid events must have a ticket price!")
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'value': '1'}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        if self.event:
            max_tickets = min(self.event.available_tickets_count, 10)
            self.fields['quantity'].widget.attrs['max'] = max_tickets
            self.fields['quantity'].help_text = f"Available tickets: {self.event.available_tickets_count}"

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        
        if self.event:
            if quantity > self.event.available_tickets_count:
                raise forms.ValidationError(f"Only {self.event.available_tickets_count} tickets available!")
            
            if quantity > 10:
                raise forms.ValidationError("Maximum 10 tickets per booking!")
        
        return quantity

class EventSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.ChoiceField(
        choices=[
            ('', 'All Dates'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.ChoiceField(
        choices=[
            ('', 'All Prices'),
            ('free', 'Free'),
            ('paid', 'Paid'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EventShareForm(forms.Form):
    platform = forms.ChoiceField(
        choices=[
            ('whatsapp', 'WhatsApp'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('email', 'Email'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )