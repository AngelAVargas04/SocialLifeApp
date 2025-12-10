from django.contrib import admin
from .models import Post, Comment, Like, Club, Profile

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'date_posted', 'get_like_count', 'get_comment_count']
    list_filter = ['date_posted']
    search_fields = ['content', 'user__username']
    readonly_fields = ['date_posted', 'slug']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'date_commented']
    list_filter = ['date_commented']
    search_fields = ['content', 'user__username']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']
    search_fields = ['user__username']
