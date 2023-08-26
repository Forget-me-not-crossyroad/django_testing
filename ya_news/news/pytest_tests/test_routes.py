from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

PK = 1


@pytest.mark.parametrize(
    'url',
    (reverse('news:edit', args=(PK,)), reverse('news:delete', args=(PK,))),
)
def test_unauthenticated_user_redirect_(client, comment, url):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    # Вторым параметром передаём note_object,
    # в котором будет либо фикстура с объектом заметки, либо None.
    'url, test_client, http_status',
    (
        (reverse('news:home'), lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:signup'), lazy_fixture('client'), HTTPStatus.OK),
        (
            reverse('news:edit', args=(PK,)),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            reverse('news:detail', args=(PK,)),
            lazy_fixture('client'),
            HTTPStatus.OK,
        ),
        (
            reverse('news:delete', args=(PK,)),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            reverse('news:edit', args=(PK,)),
            lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            reverse('news:delete', args=(PK,)),
            lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (reverse('users:login'), lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:logout'), lazy_fixture('client'), HTTPStatus.OK),
    ),
)
def test_access_for_anonymous_user(
    url,
    test_client,
    http_status,
    comment,
):
    response = test_client.get(url)
    assert response.status_code == http_status
