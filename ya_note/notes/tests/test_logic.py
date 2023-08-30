from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):

    NOTES_TEXT = 'Текст заметки'
    NOTES_TITLE = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.NOTES_TEXT, 'title': cls.NOTES_TITLE}

    def test_compare_db_and_test_data(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note_without_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        expected_slug = slugify(self.form_data['title'])
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.last()
        self.assertEqual(note.text, self.NOTES_TEXT)
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.author, self.user)

    def test_user_cant_create_note_with_used_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        expected_slug = slugify(self.form_data['title'])
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
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

    NOTES_TEXT = 'Текст заметки'
    NEW_NOTES_TEXT = 'Обновлённый комментарий'
    NOTES_TITLE = 'Заголовок1'
    NEW_NOTES_TITLE = 'Заголовок2'
    SLUG = 'zagolovok1'
    NEW_SLUG = 'zagolovok2'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author, text=cls.NOTES_TEXT, title=cls.NOTES_TITLE
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'text': cls.NEW_NOTES_TEXT,
            'title': cls.NEW_NOTES_TITLE,
        }

    def test_author_can_delete_comment(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_comment(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTES_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTES_TITLE)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

    def test_author_cant_delete_comment(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_cant_edit_comment(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTES_TEXT)
        self.assertEqual(self.note.title, self.NOTES_TITLE)
        self.assertEqual(self.note.author, self.author)
        self.assertEqual(self.note.slug, self.SLUG)
