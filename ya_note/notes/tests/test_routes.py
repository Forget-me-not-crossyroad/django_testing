# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes_slug = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст заметки',
            slug='test_theme',
        )
        cls.notes_empty_slug = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст заметки',
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                for slug in (self.notes_slug.slug, self.notes_empty_slug.slug):
                    with self.subTest(user=user, name=name):
                        url = reverse(name, args=(slug,))
                        response = user.get(url)
                        print(slug)
                        self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in (reverse('notes:edit', args=(self.notes_slug.slug,)),
                     reverse('notes:delete', args=(self.notes_slug.slug,)),
                     reverse('notes:detail', args=(self.notes_slug.slug,)),
                     reverse('notes:add'),
                     reverse('notes:list'),
                     reverse('notes:success'),
                     ):
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_all_users(self):
        for name in ('notes:home',
                     'users:signup',
                     'users:logout',
                     'users:login'
                     ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
