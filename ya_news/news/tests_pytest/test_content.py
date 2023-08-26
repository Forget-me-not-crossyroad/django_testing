from datetime import date

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm

pytestmark = pytest.mark.django_db

PK = 1


def test_client_has_form(client, admin_client, news):
    url = reverse('news:detail', args=(PK,))
    response = client.get(url)
    admin_response = admin_client.get(url)
    assert (
        isinstance(admin_response.context['form'], CommentForm)
        and 'form' not in response.context
    )


def test_news_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    news_list = list(response.context['object_list'])
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert isinstance(news_list[0].date, date)
    assert news_list == sorted(
        news_list, key=lambda time: time.date, reverse=True
    )


def test_comments_order(client, news, comments_list):
    url = reverse('news:detail', args=(PK,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    comments_list = list(news.comment_set.all())
    assert isinstance(comments_list[0].created, timezone.datetime)
    assert comments_list == sorted(
        comments_list, key=lambda time: time.created
    )
