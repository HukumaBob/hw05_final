"""Base views for authentification."""

from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Signup view."""

    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class LogOut(CreateView):
    """Logout view."""
    form_class = CreationForm
    success_url = reverse_lazy('users:password_reset_form')
    template_name = 'users/password_reset_form.html'
