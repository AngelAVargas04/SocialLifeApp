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
    # --- HANDLE POST SUBMISSION (Keep exactly as is) ---
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            
            # Slug generation logic
            content = form.cleaned_data.get('content')
            base_slug = slugify(content[:50])
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            new_post.slug = slug
            
            new_post.save()
            return redirect('home') 
    else:
        form = PostForm()

    # --- FETCH FEED DATA (Keep as is) ---
    posts = Post.objects.exclude(slug__isnull=True).exclude(slug__exact='').order_by('-date_posted')
    
  # joined club ids for the logged-in user
    joined_club_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        joined_club_ids = list(request.user.profile.clubs.values_list('id', flat=True))

    # --- RENDER TEMPLATE ---
    context = {
        'posts': posts,
        'form': form,
        'joined_club_ids': joined_club_ids, # <-- Pass the list to the template
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

@login_required
def create_club(request):
    """AJAX endpoint to create a new club"""
    if request.method == 'POST':
        import json
        from django.db import IntegrityError
        
        try:
            data = json.loads(request.body)
            club_name = data.get('name', '').strip()
            
            if not club_name:
                return JsonResponse({'success': False, 'error': 'Club name is required'})
            
            # Check if club already exists (case-insensitive)
            if Club.objects.filter(name__iexact=club_name).exists():
                return JsonResponse({'success': False, 'error': 'Name already taken'})
            
            # Create the club
            club = Club.objects.create(name=club_name)
            return JsonResponse({
                'success': True,
                'club': {
                    'id': club.id,
                    'name': club.name
                }
            })
        except IntegrityError:
            # Catch database-level uniqueness constraint violation
            return JsonResponse({'success': False, 'error': 'Name already taken'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred while creating the club'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

@login_required
def join_club(request):
    """AJAX endpoint to join a club"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        club_id = data.get('club_id')
        
        try:
            club = Club.objects.get(id=club_id)
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.clubs.add(club)
            return JsonResponse({'success': True, 'message': f'Joined club {club.name}'})
        except Club.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Club not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

