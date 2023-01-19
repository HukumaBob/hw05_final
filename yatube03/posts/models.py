"""List of main models."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Class of groups."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        """Group name."""
        return self.title


class Post(models.Model):
    """Class of posts."""

    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста'
                            )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации'
                                    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        """Posts name."""

        return self.text[:15]

    class Meta:
        """Useful Meta."""

        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """Class of posts comments."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
        help_text='Пост, к которому относится комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )    
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария'
                            )
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата публикации комментария'
                                   )

    def __str__(self):
        """Comments text."""

        return self.text[:15]

    class Meta:
        """Useful Meta."""

        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
