from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Comment, StudentProfile
from .forms import RegistrationForm, PostForm, CommentForm, StudentProfileForm

# Choices for filters – import from models or define here
from .models import DEPARTMENT_CHOICES, POST_TYPE_CHOICES


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def home(request):
    query = request.GET.get('q')
    dept_filter = request.GET.get('dept')
    type_filter = request.GET.get('type')
    
    posts = Post.objects.all()
    
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))
    if dept_filter:
        posts = posts.filter(department=dept_filter)
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'departments': DEPARTMENT_CHOICES,
        'post_types': POST_TYPE_CHOICES,
        'current_dept': dept_filter,
        'current_type': type_filter,
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Only top-level comments (parent is None)
    comments = post.comments.filter(parent=None, active=True)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form, 'title': 'Create Post'})


@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        messages.error(request, 'You are not the author.')
        return redirect('home')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_form.html', {'form': form, 'title': 'Edit Post'})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        messages.error(request, 'You are not the author.')
        return redirect('home')
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted!')
        return redirect('home')
    return render(request, 'post_confirm_delete.html', {'post': post})


@login_required
def profile(request):
    user_posts = request.user.posts.all()
    return render(request, 'profile.html', {'user_posts': user_posts})


@login_required
def edit_profile(request):
    profile = request.user.student_profile
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def upvote_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
        messages.info(request, 'Upvote removed')
    else:
        post.upvotes.add(request.user)
        messages.success(request, 'Upvoted!')
    return redirect('post_detail', slug=post.slug)


# Optional: Replace Category views with Department-based views
def department_posts(request, dept_code):
    """Show posts for a specific department (replaces category_posts)"""
    posts = Post.objects.filter(department=dept_code)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Get department display name
    dept_name = dict(DEPARTMENT_CHOICES).get(dept_code, dept_code)
    return render(request, 'department_posts.html', {
        'page_obj': page_obj,
        'department': {'code': dept_code, 'name': dept_name}
    })


def departments_list(request):
    """List all departments (replaces categories_list)"""
    departments = [{'code': code, 'name': name} for code, name in DEPARTMENT_CHOICES]
    return render(request, 'departments.html', {'departments': departments})