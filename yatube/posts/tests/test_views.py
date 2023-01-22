"""Tests of post views."""

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post

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
        cache.clear()
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
        self.author.force_login(self.user)
        self.auth_user = User.objects.create_user(username='Nobody')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def _assert_post_has_attrs(
            self, reverse_name, post, id, author,
            group, text, pub_date, image):
        """Функция для служебного использования в тестах контекста"""
        self.assertEqual(
            post.id, id, f'Ошибка словаря context на странице: {reverse_name}'
        )
        self.assertEqual(
            post.author, author,
            f'Ошибка словаря context на странице: {reverse_name}'
        )
        self.assertEqual(
            post.group, group,
            f'Ошибка словаря context на странице: {reverse_name}'
        )
        self.assertEqual(
            post.text, text,
            f'Ошибка словаря context на странице: {reverse_name}'
        )
        self.assertEqual(
            post.pub_date, pub_date,
            f'Ошибка словаря context на странице: {reverse_name}'
        )
        self.assertEqual(
            post.image, image,
            f'Ошибка словаря context на странице: {reverse_name}'
        )

    def test_page_show_correct_context(self):
        """
        Шаблоны index, group_list, profile, post_detail
        сформированы с правильным контекстом.
        """
        names_pages = {
            reverse('posts:index'):
            'page_obj',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            'page_obj',
            (reverse('posts:profile',
             kwargs={'username': self.user.username})):
            'page_obj',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'post',
        }
        cache.clear()
        for reverse_name, response_context in names_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                if response_context != 'post':
                    first_object = response.context['page_obj'][0]
                else:
                    first_object = response.context['post']
                self._assert_post_has_attrs(
                    reverse_name,
                    first_object,
                    self.post.pk,
                    self.post.author,
                    self.group,
                    self.post.text,
                    self.post.pub_date,
                    self.post.image,
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
        response = self.author.get(template)
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
        cls.comm_txt = 'Текст комментария'
        cls.comment = Comment.objects.create(
            text=cls.comm_txt,
            author=cls.user,
            post=cls.post,
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
        cache.clear()
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

    def test_comment_of_auth_user_is_possible(self):
        """Комментировать посты может только авторизованный пользователь."""
        template_page = (
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        )
        response = self.author.post(
            template_page,
            data={'text': 'Another comment'},
            follow=True,
        )
        post_instance = response.context.get('form').fields.get('text')
        self.assertIsInstance(post_instance, forms.fields.CharField)
        response = self.guest_client.post(
            template_page,
            data={'text': 'Alien comment'},
            follow=True,
        )
        post_instance = response.context.get('form').fields.get('text')
        self.assertIsNone(post_instance)

    def test_comment_appears_on_post_page(self):
        """После успешной отправки комментарий появляется на странице поста."""
        template_page = (
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk})
        )
        comm_txt = 'Bingo!'
        response = self.author.post(
            template_page,
            data={'text': comm_txt},
            follow=True,
        )
        template_page = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        )
        response = self.author.get(template_page)
        comment_text = response.context.get('comments').values('text')
        comment_text = str(comment_text)
        self.assertTrue(comm_txt in comment_text)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = Client()
        cls.user = User.objects.create_user(username='WilliamBlake')
        cls.author.force_login(cls.user)
        cls.auth_user_01 = User.objects.create_user(username='Nobody')
        cls.follower_01 = Client()
        cls.follower_01.force_login(cls.auth_user_01)
        cls.auth_user_02 = User.objects.create_user(username='ColeWilson')
        cls.follower_02 = Client()
        cls.follower_02.force_login(cls.auth_user_02)
        cls.post = Post.objects.create(
            text=(
                'If the doors of perception were cleansed, '
                'everything would appear to man as it is: infinite.'
            ),
            author=cls.user,
        )

    def test_auth_user_can_follow_and_unfollow(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок.
        """
        template_page = {
            'Follow_page':
            reverse('posts:follow_index'),
            'Subscribe':
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}),
            'Unsubscribe':
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username})
        }
        self.follower_01.post(
            template_page['Subscribe'],
            data={'author': self.author, 'following': True},
            follow=True
        )
        responce = self.follower_01.get(template_page['Follow_page'])
        subscribe_add = len(responce.context.get('page_obj').object_list)
        self.follower_01.post(
            template_page['Unsubscribe'],
            data={'author': self.author, 'following': False},
            follow=True
        )
        responce = self.follower_01.get(template_page['Follow_page'])
        subscribe_delete = len(responce.context.get('page_obj').object_list)
        self.assertTrue(subscribe_add - subscribe_delete == 1)

    def test_author_following_only_by_followers(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан.
        """
        template_page = {
            'Follow_page':
            reverse('posts:follow_index'),
            'Subscribe':
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}),
        }
        responce = self.follower_01.post(
            template_page['Subscribe'],
            data={'author': self.author, 'following': True},
            follow=True
        )
        responce = self.follower_01.get(template_page['Follow_page'])
        post_object_01 = len(responce.context.get('page_obj').object_list)
        responce = self.follower_02.get(template_page['Follow_page'])
        post_object_02 = len(responce.context.get('page_obj').object_list)
        self.assertTrue(post_object_01 - post_object_02 == 1)
