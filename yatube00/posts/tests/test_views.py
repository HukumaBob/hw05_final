"""Tests of post views."""

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()

NUMBER_OF_POSTS = 13
POSTS_PER_PAGE = 10


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Просто название',
            slug='test-slug',
            description='Описание простого поста',
        )

        cls.user = User.objects.create_user(username='WilliamBlake')
        for i in range(NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'Просто тестовый текст #{i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def _test_paginator(self, posts_cnt, url_addon):
        """Функция ДСП для пажинатора."""
        templates_page_names = (
            reverse('posts:index') + url_addon,
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + url_addon,
            reverse('posts:profile', kwargs={'username': self.user.username})
            + url_addon,
        )
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), posts_cnt)

    def test_first_page_contains_ten_records(self):
        '''Пажинатор на первой странице'''
        self._test_paginator(POSTS_PER_PAGE, '')

    def test_second_page_contains_three_records(self):
        '''Пажинатор на последней странице'''
        self._test_paginator(NUMBER_OF_POSTS - POSTS_PER_PAGE, '?page=2')


class PostViewsTest(TestCase):
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
            text='Просто тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostViewsTest.user)
        self.auth_user = User.objects.create_user(username='Nobody')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def _assert_post_has_attrs(self, post, id, author, group, text):
        """Функция для служебного использования в тестах контекста"""
        self.assertEqual(post.id, id)
        self.assertEqual(post.author, author)
        self.assertEqual(post.group, group)
        self.assertEqual(post.text, text)

    def test_page_show_correct_context(self):
        """
        Шаблоны index, group_list, profile
        сформированы с правильным контекстом.
        """
        templates_page_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for reverse_name in templates_page_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self._assert_post_has_attrs(
                    first_object,
                    self.post.pk,
                    self.post.author,
                    self.group,
                    self.post.text,
                )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """
        Шаблон post_create/фильтр по id сформирован с правильным контекстом.
        """
        template = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.get(template)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Одна группа',
            slug='test-slug',
            description='Описание одной группы',
        )

        cls.group_another = Group.objects.create(
            title='Другая группа',
            slug='test-another_slug',
            description='Описание другой группы',
        )

        cls.user = User.objects.create_user(username='WilliamBlake')
        cls.post = Post.objects.create(
            text='Просто тестовый текст',
            author=cls.user,
            group=cls.group,
        )

        cls.post_another = Post.objects.create(
            text='Другой тестовый текст',
            author=cls.user,
            group=cls.group_another,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.auth_user = User.objects.create_user(username='Nobody')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def test_post_of_selected_group_appeare_in_pages(self):
        """Пост с указанием группы появляется на страницах"""
        templates_page_names = {
            'Home page': reverse('posts:index'),
            'Group list':
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'Profile':
            reverse('posts:profile', kwargs={'username': self.user.username}),
        }
        for page, reverse_name in templates_page_names.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse_name)
                post_objects = response.context.get('page_obj').object_list
                self.assertIn(self.post, post_objects)

    def test_post_of_another_group_didnt_appeare_in_pages(self):
        """Пост из одной группы не появляется на страницах другой группы"""
        template_page = (reverse('posts:group_list',
                         kwargs={'slug': self.group_another.slug}))
        response = self.authorized_client.get(template_page)
        post_object = (response.context.get('page_obj').object_list[0])
        self.assertNotEqual(post_object, self.post)
