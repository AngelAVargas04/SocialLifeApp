from django.urls import path
from . import views
#from django.contrib.auth import views as auth_views # Import Django's views

urlpatterns = [
    path('', views.home, name='home'),
    
    # NEW: Use Django's built-in LoginView. 
    # It automatically handles form validation and authentication.
    # NEW NEW: Took it out (Josue)
    #path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # NEW: Also include the logout path for completeness
    # NEW NEW: Took it out (Josue)
    #path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), 
    
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]