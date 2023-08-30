from http import HTTPStatus
from random import choice

import pytest
from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

PK = 1

reverse('news:home'),
reverse('news:detail', args=(PK,)),
reverse('news:edit', args=(PK,)),
reverse('news:delete', args=(PK,)),
reverse('users:login'),
reverse('users:logout'),
reverse('users:signup'),


def test_anonymous_user_cant_create_comment(client, form_data):
    url_detail = reverse('news:edit', args=(PK,))
    expected_count = Comment.objects.count()
    client.post(url_detail, data=form_data)
    comments_count = Comment.objects.count()
    assert expected_count == comments_count


def test_user_can_create_comment(author_client, form_data, author, news):
    url_detail = reverse('news:detail', args=(PK,))
    expected_count = Comment.objects.count() + 1
    response = author_client.post(url_detail, data=form_data)
    comments_count = Comment.objects.count()
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{url_detail}#comments')
    assert expected_count == comments_count
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_user_cant_use_bad_words(author_client, news, word=choice(BAD_WORDS)):
    url_detail = reverse('news:detail', args=(PK,))
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


def test_author_can_delete_comment(author_client, comment, pk_news):
    url_detail = reverse('news:detail', args=(PK,))
    url_delete = reverse('news:delete', args=(PK,))
    expected_count = Comment.objects.count() - 1
    response = author_client.delete(url_delete)
    comments_count = Comment.objects.count()
    assertRedirects(response, f'{url_detail}#comments')
    assert expected_count == comments_count


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    url_delete = reverse('news:delete', args=(PK,))
    expected_count = Comment.objects.count()
    response = admin_client.delete(url_delete)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count


def test_author_can_edit_comment(
    author, author_client, comment, pk_news, form_data
):
    expected_count = Comment.objects.count()
    url_detail = reverse('news:detail', args=(PK,))
    url_edit = reverse('news:edit', args=(PK,))
    response = author_client.post(url_edit, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert expected_count == comments_count
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    author, admin_client, comment, pk_news, form_data
):
    url_edit = reverse('news:edit', args=(PK,))
    expected_count = Comment.objects.count()
    response = admin_client.post(url_edit, data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
