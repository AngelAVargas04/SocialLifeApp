from django import forms
from .models import Post

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