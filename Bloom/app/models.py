from django.db import models
from django.contrib.auth import get_user_model # To be able to identify the user making the post

User = get_user_model()     # Get the active User model for the project

# Create your models here.
class Post(models.Model):
    # LINK TO USER
    # Associates the post with the user who created it.
    # on_delete=models.CASCADE means if the User is deleted, their posts are deleted too.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # POST CONTENT
    # Changed 'subject' to 'title' and limited 'description' to a tweet-like length
    title = models.CharField(max_length=100, blank=True, null=True)
    
    # Content of the post. Max length
    content = models.TextField(max_length=280) 

    likes = models.PositiveIntegerField(default=0)  # Count of likes

    comments = models.PositiveIntegerField(default=0)  # Count of comments
    
    
    # SLUG FIELD (Optional for social media, often used for detailed post pages)
    slug = models.SlugField(unique=True)
    
    # TIMESTAMP
    date_posted = models.DateTimeField(auto_now_add=True)

    # METADATA
    class Meta:
        # Orders posts by date, newest first (descending order)
        ordering = ['-date_posted'] 
        verbose_name = "Social Post"

    def __str__(self):
        # Displays the username and the start of the content
        return f"{self.user.username}: {self.content[:20]}..."
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    date_commented = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_commented']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.slug}"