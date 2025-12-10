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

  # trying to add like and comment functionality (edgar)

    def get_like_count(self):
        """Get the total number of likes for this post"""
        return self.likes.count()
    
    def is_liked_by_user(self, user):
        """Check if a specific user has liked this post"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def get_comment_count(self):
        """Get the total number of comments for this post"""
        return self.post_comments.count()

class Like(models.Model):
    """Model to track which users liked which posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only like a post once
        unique_together = ['post', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.slug}"
    
class Comment(models.Model):
    """Model for comments on posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    date_commented = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_commented']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.slug}"

class Club(models.Model):
    """Model for clubs that users can search and join"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Club"
        verbose_name_plural = "Clubs"
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    """Extended user profile with profile picture"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default=None)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_profile_picture_url(self):
        """Get the profile picture URL or a default"""
        if self.profile_picture:
            return self.profile_picture.url
        return None  # Return None to use default placeholder in template