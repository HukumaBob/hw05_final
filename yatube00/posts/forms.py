"""Useful forms for creating new posts."""

from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Model for new post/editing."""

    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Empty field!')
        return data
