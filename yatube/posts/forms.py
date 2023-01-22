"""Useful forms for creating new posts."""
from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Model for new post/editing."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Empty field!')
        return data


class CommentForm(forms.ModelForm):
    """Model for posts comment."""

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Empty field!')
        return data
