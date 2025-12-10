from django import forms
from .models import Post, Comment, Profile

class PostForm(forms.ModelForm):
    # Customize the appearance of the content
    content = forms.CharField(
        label='', # Remove the default label
        widget=forms.Textarea(attrs={
            'rows': 4, # Make the text area larger
            'placeholder': 'What are you doing today?', # Placeholder text
            'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500' 
            # Add Tailwind classes for styling
        })
    )
    
    # Optional: Customize the title field (since a post might not have one)
    title = forms.CharField(
        required=False, # Make the title optional
        label='Title (Optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Add an optional title',
            'class': 'w-full p-2 border rounded-lg mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content'] # Fields the user fills out
        # Note: 'user', 'date_posted', and 'slug' are handled automatically in the view

class CommentForm(forms.ModelForm):
    """Form for creating comments on posts"""
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Write a comment...',
            'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = Comment
        fields = ['content']
        # Note: 'user' and 'post' are handled automatically in the view

class ProfilePictureForm(forms.ModelForm):
    """Form for uploading profile picture"""
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'profile-picture-input'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['profile_picture']