"""Tests of post forms."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Просто название группы',
            slug='test-slug',
            description='Описание группы',
        )

        cls.user = User.objects.create_user(username='WilliamBlake')
        cls.post = Post.objects.create(
            text='Первый тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostCreateFormTests.user)
        self.auth_user = User.objects.create_user(username='Nobody')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def test_create_post_new_record_in_db(self):
        '''При отправке формы 'create_post' создаётся новая запись в БД.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Второй тестовый текст',
            'group': self.group.pk
        }
        response = self.author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.pk, form_data['group'])
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_change_record_in_db(self):
        '''При отправке формы c 'post_edit' измененяется пост/post_id в БД.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Третий тестовый текст',
        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        post_changed = Post.objects.get(id=self.post.pk)
        self.assertEqual(post_changed.text, form_data['text'])
        self.assertEqual(post_changed.author, self.post.author)
        self.assertEqual(response.status_code, HTTPStatus.OK)
