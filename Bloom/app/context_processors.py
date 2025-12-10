from .models import Club

def clubs_context(request):
    """Make clubs available in all templates"""
    clubs_list = Club.objects.all().values_list('name', flat=True)
    clubs_objects = Club.objects.all()
    return {
        'clubs': list(clubs_list),  # For JSON script in navbar
        'clubs_objects': clubs_objects  # For displaying in templates
    }

