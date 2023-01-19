"""Tests of post URLs."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Просто название',
            slug='test-slug',
            description='Описание простого поста',
        )

        cls.post = Post.objects.create(
            text='Просто текст',
            author=User.objects.create_user(username='WilliamBlake'),
            group=cls.group,
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.author = self.post.author
        self.autorized_author = Client()
        self.autorized_author.force_login(self.author)
        self.user = User.objects.create_user(username='Nobody')
        self.autorized_user = Client()
        self.autorized_user.force_login(self.user)

    def test_url_exists_at_desired_location_for_author(self):
        """Cтраницы доступны (или недоступны) автору."""
        url_pages_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url_pages, url_status in url_pages_status.items():
            with self.subTest(url_pages=url_pages):
                response = self.autorized_author.get(url_pages)
                self.assertEqual(response.status_code, url_status.value)

    def test_url_exists_at_desired_location_for_authorized_user(self):
        """Cтраницы доступны (или недоступны) авторизированному юзеру."""
        url_pages_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url_pages, url_status in url_pages_status.items():
            with self.subTest(url_pages=url_pages):
                response = self.autorized_user.get(url_pages)
                self.assertEqual(response.status_code, url_status.value)

    def test_url_exists_at_desired_location_for_unauthorized_user(self):
        """
        Страницы доступны (или недоступны) неавторизированному юзеру.
        """
        url_pages_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url_pages, url_status in url_pages_status.items():
            with self.subTest(url_pages=url_pages):
                response = self.guest_client.get(url_pages)
                self.assertEqual(response.status_code, url_status.value)

    def test_url_reverse_adressing_for_author(self):
        """Cтраницы переадресации автору."""
        url_to_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            (reverse('posts:profile',
             kwargs={'username': self.author.username})):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for url_pages, template in url_to_template.items():
            with self.subTest(url_pages=url_pages):
                response = self.autorized_author.get(url_pages)
                self.assertTemplateUsed(response, template)

    def test_url_reverse_adressing_for_auth_user(self):
        """Cтраницы переадресации авторизованному юзеру."""
        url_to_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            (reverse('posts:profile',
             kwargs={'username': self.author.username})):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for url_pages, template in url_to_template.items():
            with self.subTest(url_pages=url_pages):
                response = self.autorized_user.get(url_pages, follow=True)
                if response.status_code == 200:
                    self.assertTemplateUsed(response, template)
                elif response.status_code == 302:
                    self.assertRedirects(response, template)

    def test_url_adressing_for_unauth_user(self):
        """Cтраницы переадресации неавторизованному юзеру."""
        url_to_template = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            reverse('posts:post_create'): '/auth/login/?next=/create/',
        }
        for url_pages, template in url_to_template.items():
            with self.subTest(url_pages=url_pages):
                response = self.guest_client.get(url_pages, follow=True)
                self.assertRedirects(response, template)
