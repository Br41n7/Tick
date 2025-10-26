from django import forms
from .models import ArtistProfile, Reel

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = ArtistProfile
        fields = [
            'stage_name', 'bio', 'genre', 'profile_image', 'cover_image',
            'instagram_handle', 'twitter_handle', 'tiktok_handle',
            'youtube_channel', 'spotify_link', 'apple_music_link',
            'booking_email', 'phone_number'
        ]
        widgets = {
            'stage_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Afrobeats, Hip-hop, R&B'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'instagram_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'twitter_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'tiktok_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'youtube_channel': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
            'spotify_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://spotify.com/...'}),
            'apple_music_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://music.apple.com/...'}),
            'booking_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_stage_name(self):
        stage_name = self.cleaned_data['stage_name']
        # Check if stage name is unique (excluding current instance)
        queryset = ArtistProfile.objects.filter(stage_name__iexact=stage_name)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("An artist with this stage name already exists!")
        return stage_name

    def clean_instagram_handle(self):
        handle = self.cleaned_data['instagram_handle'].strip()
        if handle and not handle.startswith('@'):
            handle = f'@{handle}'
        return handle

    def clean_twitter_handle(self):
        handle = self.cleaned_data['twitter_handle'].strip()
        if handle and not handle.startswith('@'):
            handle = f'@{handle}'
        return handle

    def clean_tiktok_handle(self):
        handle = self.cleaned_data['tiktok_handle'].strip()
        if handle and not handle.startswith('@'):
            handle = f'@{handle}'
        return handle

class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = [
            'title', 'description', 'content_type', 'video_file', 
            'image_file', 'thumbnail', 'allow_comments', 'allow_downloads'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'image_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_downloads': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        video_file = cleaned_data.get('video_file')
        image_file = cleaned_data.get('image_file')
        
        if content_type == 'video' and not video_file:
            raise forms.ValidationError("Video content type requires a video file!")
        
        if content_type == 'image' and not image_file:
            raise forms.ValidationError("Image content type requires an image file!")
        
        return cleaned_data

    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Check file size (max 50MB for videos)
            if video_file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("Video file size cannot exceed 50MB!")
            
            # Check file extension
            valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
            file_extension = video_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in valid_extensions:
                raise forms.ValidationError("Invalid video file format!")
        
        return video_file

    def clean_image_file(self):
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            # Check file size (max 10MB for images)
            if image_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 10MB!")
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_extension = image_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in valid_extensions:
                raise forms.ValidationError("Invalid image file format!")
        
        return image_file

class ArtistSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search artists...'
        })
    )
    genre = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Genre (e.g., Afrobeats, Hip-hop)'
        })
    )
    sort = forms.ChoiceField(
        choices=[
            ('followers', 'Most Followers'),
            ('reels', 'Most Reels'),
            ('views', 'Most Views'),
            ('newest', 'Newest'),
            ('verified', 'Verified Only'),
        ],
        required=False,
        initial='followers',
        widget=forms.Select(attrs={'class': 'form-control'})
    )