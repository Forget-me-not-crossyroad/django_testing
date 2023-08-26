# news/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NOTES_TEXT = 'Текст заметки'
    NOTES_TITLE = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # cls.notes = Note.objects.create(title='Заголовок',
        #                                 text='Текст',
        #                                 author=cls.user,)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'text': cls.NOTES_TEXT, 'title': cls.NOTES_TITLE}

    def test_compare_db_and_test_data(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Создаем ожидаемый slug
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, self.url_success)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты заметки совпадают с ожидаемыми.
        self.assertEqual(note.text, self.NOTES_TEXT)
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.user)

    def test_user_cant_create_note_with_used_slug(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Создаем ожидаемый slug
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, self.url_success)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        self.assertFormError(
            self.auth_client.post(self.url, data=self.form_data),
            form='form',
            field='slug',
            errors=(expected_slug + WARNING),
            msg_prefix=(
                f'Убедитесь, что форма создания заметки, возвращает '
                f'ошибку "{WARNING}" при попытке создать заметку с '
                f'существующим slug.'
            ),
        )


class TestNoteAddEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
    NOTES_TEXT = 'Текст заметки'
    NEW_NOTES_TEXT = 'Обновлённый комментарий'
    NOTES_TITLE = 'Заголовок1'
    NEW_NOTES_TITLE = 'Заголовок2'

    @classmethod
    def setUpTestData(cls):
        # Создаём запись в БД.
        # Формируем адрес блока с комментариями,
        # который понадобится для тестов.
        # Создаём пользователя - автора комментария.
        cls.author = User.objects.create(username='Автор комментария')
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём объект комментария.
        cls.note = Note.objects.create(
            author=cls.author, text=cls.NOTES_TEXT, title=cls.NOTES_TITLE
        )
        # URL для редактирования комментария.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления комментария.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # URL success
        cls.success_url = reverse('notes:success')
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {
            'text': cls.NEW_NOTES_TEXT,
            'title': cls.NEW_NOTES_TITLE,
        }

    def test_author_can_delete_comment(self):
        notes_count = Note.objects.count()
        # В начале теста в БД всегда есть 1 комментарий,
        # созданный в setUpTestData.
        self.assertEqual(notes_count, 1)
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, self.success_url)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_comment(self):
        notes_count = Note.objects.count()
        # В начале теста в БД всегда есть 1 комментарий,
        # созданный в setUpTestData.
        self.assertEqual(notes_count, 1)
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.success_url)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст и заголовок
        # комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTES_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTES_TITLE)

    def test_author_cant_delete_comment(self):
        notes_count = Note.objects.count()
        # В начале теста в БД всегда есть 1 комментарий,
        # созданный в setUpTestData.
        self.assertEqual(notes_count, 1)
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 1)

    def test_author_cant_edit_comment(self):
        notes_count = Note.objects.count()
        # В начале теста в БД всегда есть 1 комментарий,
        # созданный в setUpTestData.
        self.assertEqual(notes_count, 1)
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст и заголовок
        # комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NOTES_TEXT)
        self.assertEqual(self.note.title, self.NOTES_TITLE)
