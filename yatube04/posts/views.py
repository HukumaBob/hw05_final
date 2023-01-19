"""List of main models."""

from django.core.paginator import Paginator
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from .models import Group, Post, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


POSTS_PER_PAGE = 10

User = get_user_model()


def get_page_context(queryset, request):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Prepare data for the group-list page."""
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Prepare data for the user profile page."""

    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    following = (
        Follow.objects.filter(user_id=request.user.id,
                              author_id=author.id)
    ).exists()
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, template, context)


def post_detail(request, post_id):
    """Prepare data for the post details page."""

    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    "Fresh post."
    template = 'posts/create_post.html'
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author_id = request.user.id
            post.save()
            return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()    
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user  
    author = Follow.objects.filter(user_id=request.user.id).values('author_id')    
    authors = Post.objects.filter(author_id__in=author)
    print(authors.values('author_id'))
    context = get_page_context(authors, request)
    #context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора

    template = 'posts/profile.html'
    author = User.objects.get(username=username)
    Follow.objects.create(author_id=author.id, user_id=request.user.id)
    context = {
        'author': author,
        'following': True,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, template, context)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    template = 'posts/profile.html'
    author = User.objects.get(username=username)
    obj = get_object_or_404(
        Follow, author_id=author.id,
        user_id=request.user.id
    )
    obj.delete()
    context = {
        'author': author,
        'following': False,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, template, context)