from .models import Club, Profile

def clubs_context(request):
    """Make clubs available in all templates"""
    clubs_list = Club.objects.all().values_list('name', flat=True)
    clubs_objects = Club.objects.all()
    
    # Get user's club IDs for membership checking
    user_club_ids = []
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        # Re-fetch the clubs relationship to ensure we get fresh data
        # refresh_from_db() doesn't work for ManyToMany, so we need to re-query
        user_club_ids = list(Profile.objects.filter(user=request.user).values_list('clubs__id', flat=True).distinct())
        # Filter out None values in case user has no clubs
        user_club_ids = [cid for cid in user_club_ids if cid is not None]
    
    return {
        'clubs': list(clubs_list),  # For JSON script in navbar
        'clubs_objects': clubs_objects,  # For displaying in templates
        'user_club_ids': user_club_ids,  # List of club IDs the user is a member of
    }

