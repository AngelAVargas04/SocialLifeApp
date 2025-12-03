from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.utils.text import slugify # <--- NEW IMPORT
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
@login_required
def home(request):
    # HANDLE POST SUBMISSION 
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = PostForm(request.POST)
        if form.is_valid():
            # Save the form data, but don't commit to the database yet
            new_post = form.save(commit=False)
            
            # Manually set the user field to the current logged-in user
            new_post.user = request.user
            
            # ⭐ SLUG GENERATION LOGIC ADDED HERE ⭐
            
            # 1. Determine the source text for the slug (use content, as title is optional)
            content = form.cleaned_data.get('content')
            # Use only the first 50 chars of content for a clean slug
            base_slug = slugify(content[:50])
            
            # 2. Check for uniqueness and append a counter if needed
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            new_post.slug = slug
            # ⭐ END SLUG GENERATION LOGIC ⭐

            new_post.save()
            # Redirect to the home page to prevent form resubmission
            return redirect('home') 
    else:
        # HANDLE GET REQUEST (Display the page)
        form = PostForm()

    # FETCH DATA FOR THE FEED 
    # Fetch all posts from the database (ordered by '-date_posted' from your model's Meta class)
    posts = Post.objects.all() 
    
    # RENDER TEMPLATE
    context = {
        'posts': posts, # Pass the list of posts to the template
        'form': form,   # Pass the post creation form to the template
    }
    return render(request, 'home.html', context)

#Removed (Josue)
#def login(request):
#   return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        # 1. Populate the form with submitted data
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            # 2. Save the new user to the database
            user = form.save()
            
            # Optional: Automatically log the user in after registration (requires 'login' import)
            # login(request, user) 
            
            # 3. Redirect to the login page or the homepage
            return redirect('login') # Redirects to the login page after successful registration
    
    else:
        # 4. Handle GET request: Display an empty form
        form = UserCreationForm()
        
    # Pass the form to the template
    return render(request, 'signup.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')