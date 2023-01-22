"""Tests of post forms."""

import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Первый тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_new_record_in_db(self):
        '''При отправке формы 'create_post' создаётся новая запись в БД.'''
        posts_count = Post.objects.count()
        template = reverse('posts:post_create')
        self.uploaded.name = 'post_create.gif'
        form_data = {
            'text': 'Второй тестовый текст',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        response = self.author.post(
            template,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.pk, form_data['group'])
        self.assertEqual(
            last_post.image.name,
            f'posts/{form_data["image"].name}'
        )
        self.assertTrue(
            Post.objects.filter(image=f'posts/{form_data["image"].name}').
            exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_change_record_in_db(self):
        '''При отправке формы c 'post_edit' измененяется пост/post_id в БД.'''
        posts_count = Post.objects.count()
        template = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        self.uploaded.name = 'post_edit.gif'
        form_data = {
            'text': 'Третий тестовый текст',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        response = self.author.post(
            template,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.pk, form_data['group'])
        self.assertEqual(
            last_post.image.name,
            f'posts/{form_data["image"].name}'
        )
        self.assertTrue(
            Post.objects.filter(image=f'posts/{form_data["image"].name}').
            exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
