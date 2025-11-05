from django.shortcuts import render

def home_page(request):
    """
    Renders the home.html template and passes data to it.
    """
    context = {
        # 'title' and 'content' match the variables used in home.html
        'title': 'HEB>>>>COSTCO',
        'content': 'CLUBSONLY.',
    }
    
    # Renders the template located at social_features/templates/social_features/home.html
    return render(request, 'home.html', context)