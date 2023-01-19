import shutil
import tempfile
from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, Comment

POST_COUNT = 10

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим записи в БД для проверки доступности адресов
        cls.auth = User.objects.create_user(username='auth')
        cls.auth_user = User.objects.create_user(username='Nobody')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.auth_user)        
        cls.group = Group.objects.create(
            title='Тестовая группа №1',
            slug='test-slug1',
            description='Тестовое описание №1',
        )
        # картинка для теста
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост о разном',
            group=cls.group,
            image=uploaded,
        )
        Comment.objects.create(
            post=cls.post,
            author=cls.auth,
            text='Тестовый коммент',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

        # Проверяем, что словарь context страниц index, group_list и profile
    # в первом элементе списка object_list содержат ожидаемые значения
    def test_index_group_profile_pages_show_correct_context(self):
        """Шаблоны страниц index, group_list и profile сформированы
        с правильным контекстом.
        """

        names_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.auth.username}),
        ]
        for reverse_name in names_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
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
                    author_0, self.auth,
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

# ...тесты далее.