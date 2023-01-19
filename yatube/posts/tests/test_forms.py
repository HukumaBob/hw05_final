"""Tests of post forms."""

import os
import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post
from django.core.cache import cache

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
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='WilliamBlake')
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Первый тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.pk, form_data['group'])
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())
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

    def test_index_group_profile_pages_show_correct_context(self):
        """Шаблоны страниц index, group_list и profile сформированы
        с правильным контекстом.
        """

        names_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            (reverse('posts:profile',
             kwargs={'username': self.user.username}))
        ]
        cache.clear()
        for reverse_name in names_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                first_object = response.context['page_obj'][0]
                text_0 = first_object.text
                created_0 = first_object.pub_date
                author_0 = first_object.author
                group_0 = first_object.group
                id_0 = first_object.id
                image_0 = first_object.image

                self.assertEqual(
                    text_0, self.post.text,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    created_0, self.post.pub_date,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    author_0, self.user,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    group_0, self.group,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    id_0, self.post.id,
                    'Ошибка словаря context на странице: ' + reverse_name)
                self.assertEqual(
                    image_0, self.post.image,
                    'Ошибка словаря context на странице: ' + reverse_name)
