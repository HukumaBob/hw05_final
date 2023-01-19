"""List of main models."""

from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404, render, redirect

from .models import Group, Post

from .forms import PostForm

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
    context = {
        'author': author,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, template, context)


def post_detail(request, post_id):
    """Prepare data for the post details page."""

    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    "Fresh post."
    template = 'posts/create_post.html'
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
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
    template = 'posts/update_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            post.author_id = request.user.id
            post.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form})
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)
