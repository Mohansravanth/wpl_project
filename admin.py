from django.contrib import admin
from .models import Post, Comment, StudentProfile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'department', 'post_type', 'created_at', 'is_announcement']
    list_filter = ['department', 'post_type', 'is_announcement']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'active']
    list_filter = ['active']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_no', 'department', 'year']
    list_filter = ['department', 'year']
    search_fields = ['user__username', 'enrollment_no']