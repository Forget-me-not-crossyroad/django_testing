from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Autor')


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст новости')
    return news or None


@pytest.fixture
def pk_news(news):
    return (news.pk,)


@pytest.fixture
def comments_list(author, news):
    for i in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
    return comments_list


@pytest.fixture
def news_list():
    news_list = News.objects.bulk_create(
        News(
            title=f'Заголовок {i}',
            text='Текст новости',
            date=datetime.today().date() - timedelta(days=i),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_list or None


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT,
    )
    return comment or None


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Новый текст комментария'
