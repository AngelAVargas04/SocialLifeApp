from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Post, Club, Profile, Like, Comment 
from .forms import PostForm, ProfilePictureForm
from django.utils.text import slugify # <--- NEW IMPORT
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
import os

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
    posts = Post.objects.exclude(slug__isnull=True).exclude(slug__exact='').order_by('-date_posted')
    
    # RENDER TEMPLATE
    # Note: 'clubs' is automatically available via context processor (app.context_processors.clubs_context)
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

@login_required
def profile(request):
    """Profile page with ability to update profile picture"""
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfilePictureForm(instance=profile_obj)
    
    return render(request, 'profile.html', {'form': form})

@login_required
def update_profile_picture(request):
    """AJAX endpoint to update profile picture"""
    if request.method == 'POST':
        profile_obj, created = Profile.objects.get_or_create(user=request.user)
        
        # Delete old picture if it exists and new one is being uploaded
        if 'profile_picture' in request.FILES:
            if profile_obj.profile_picture:
                old_path = profile_obj.profile_picture.path
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            profile_obj.profile_picture = request.FILES['profile_picture']
            profile_obj.save()
            
            return JsonResponse({
                'success': True,
                'profile_picture_url': profile_obj.profile_picture.url
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def remove_profile_picture(request):
    """AJAX endpoint to remove profile picture"""
    if request.method == 'POST':
        try:
            profile_obj = Profile.objects.get(user=request.user)
            
            # Delete the file if it exists
            if profile_obj.profile_picture:
                old_path = profile_obj.profile_picture.path
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Remove the profile picture from the profile
            profile_obj.profile_picture = None
            profile_obj.save()
            
            return JsonResponse({'success': True})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Profile not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def logout_view(request):
    """Custom logout view that redirects to login page"""
    logout(request)
    return redirect('login')

def search_clubs(request):
    """AJAX endpoint for searching clubs"""
    query = request.GET.get('q', '').strip().lower()
    
    if query:
        # Filter clubs that match the search query
        clubs = Club.objects.filter(name__icontains=query)[:10]
    else:
        # Return all clubs if no query
        clubs = Club.objects.all()[:10]
    
    club_list = [{'id': club.id, 'name': club.name} for club in clubs]
    return JsonResponse({'clubs': club_list})

def aboutus(request):
    """About Us page with all Bloom information"""
    return render(request, 'aboutus.html')

@login_required
def like_post(request, slug):
    """AJAX endpoint to like or unlike a post"""
    
    # 1. Check for POST method for security and idempotence
    if request.method != 'POST':
        # Return a 405 Method Not Allowed error for non-POST requests
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    post = get_object_or_404(Post, slug=slug)
    user = request.user
    
    # Check if the user has already liked the post
    existing_like = post.likes.filter(user=user).first()
    
    if existing_like:
        # User has liked the post before, so unlike it
        existing_like.delete()
        liked = False
    else:
        # User has not liked the post, so create a new like
        # The Like model handles the creation logic
        post.likes.create(user=user)
        liked = True
    
    # Return the updated state
    return JsonResponse({
        'liked': liked,
        'like_count': post.get_like_count()
    })

@login_required
def add_comment(request, slug):
    """AJAX endpoint to add a comment to a post"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if content:
            comment = post.post_comments.create(
                user=request.user,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'user': comment.user.username,
                    'content': comment.content,
                    'date_commented': comment.date_commented.strftime('%Y-%m-%d %H:%M')
                },
                'comment_count': post.get_comment_count()
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
