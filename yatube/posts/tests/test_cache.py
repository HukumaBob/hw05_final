"""Tests of cache."""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='WilliamBlake')
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Simpliest text in the world',
            author=cls.user,
        )

    def test_cache(self):
        cache.clear()
        template = reverse('posts:index')
        response01 = self.author.get(template).content
        Post.objects.get(pk=1).delete()
        response02 = self.author.get(template).content
        self.assertEqual(response01, response02)
        cache.clear()
        response03 = self.author.get(template).content
        self.assertNotEqual(response01, response03)
