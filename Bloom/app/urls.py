from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Import Django's views

urlpatterns = [
    path('', views.home, name='home'),
    
    # NEW: Use Django's built-in LoginView. 
    # It automatically handles form validation and authentication.
    # NEW NEW: Took it out (Josue)
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # NEW: Also include the logout path for completeness
    # NEW NEW: Took it out (Josue)
    path('logout/', views.logout_view, name='logout'), 
    
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('search-clubs/', views.search_clubs, name='search_clubs'),
    path('create-club/', views.create_club, name='create_club'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('remove-profile-picture/', views.remove_profile_picture, name='remove_profile_picture'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('like-post/<slug:slug>/', views.like_post, name='like_post'),
]