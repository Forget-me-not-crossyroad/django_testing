# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату.
        # Создаём двух пользователей с разными именами:
        cls.first_author = User.objects.create(username='Первый Пользователь')
        cls.second_author = User.objects.create(username='Второй Пользователь')
        cls.list_url = reverse(
            'notes:list',
        )
        # От имени пользователя создаём заметку:

        cls.all_notes_first_author = Note.objects.bulk_create(
            Note(
                title=f'Заголовок_{index}',
                author=cls.first_author,
                text='Интересная заметка',
                slug=f'readable_note_{index}',
            )
            for index in range(2)
        )

        cls.all_notes_second_author = Note.objects.bulk_create(
            Note(
                title=f'Заголовок_{index}',
                author=cls.second_author,
                text='Интересная заметка',
                slug=f'interesting_note_{index}',
            )
            for index in range(2)
        )

    def test_access_to_notes_of_other_user(self):
        users_statuses = (
            (self.first_author, 'all_notes_first_author'),
            (self.second_author, 'all_notes_second_author'),
        )
        for user, list in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            response = self.client.get(self.list_url)
            # Проверяем, что объект новости находится в словаре контекста
            # под ожидаемым именем - названием модели.
            with self.subTest(user=user):
                self.assertNotIn(list, response.context)


# @skip(reason='Outdated tests')
class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Вычисляем текущую дату.
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Первый Пользователь')
        cls.notes_slug = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст заметки',
            slug='test_theme',
        )
        cls.edit_url = reverse('notes:edit', args=(cls.notes_slug.slug,))
        cls.add_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for name in (self.edit_url, self.add_url):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIn('form', response.context)
