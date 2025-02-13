#flake8: noqa
import uuid
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus

import pytest

from ugc_service.tests.functional.fixtures.common import unique_bookmark_data

pytestmark = pytest.mark.asyncio

BASE_BOOKMARKS_ENDPOINT = '/api/v1/ugc/bookmarks'


async def test_create_bookmark(make_post_request, valid_token, unique_bookmark_data):
    response, _, status = await make_post_request(
        BASE_BOOKMARKS_ENDPOINT,
        json=unique_bookmark_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK
    assert 'id' in response
    assert 'user_id' in response
    assert 'film_id' in response
    assert 'timestamp' in response
    assert response['film_id'] == unique_bookmark_data['film_id']
    try:
        datetime.fromisoformat(response['timestamp'].replace('Z', ''))
    except ValueError:
        pytest.fail('Invalid ISO timestamp')


async def test_create_bookmark_duplicate(make_post_request, valid_token, unique_bookmark_data):
    _, _, status1 = await make_post_request(
        BASE_BOOKMARKS_ENDPOINT,
        json=unique_bookmark_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status1 == HTTPStatus.OK

    _, _, status2 = await make_post_request(
        BASE_BOOKMARKS_ENDPOINT,
        json=unique_bookmark_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status2 == HTTPStatus.CONFLICT


async def test_get_bookmark(make_post_request, make_get_request, valid_token, unique_bookmark_data):
    create_response, _, _ = await make_post_request(
        BASE_BOOKMARKS_ENDPOINT,
        json=unique_bookmark_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    bookmark_id = create_response['id']

    response, _, status = await make_get_request(
        f'{BASE_BOOKMARKS_ENDPOINT}/{bookmark_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK
    assert response['id'] == bookmark_id
    assert response['film_id'] == unique_bookmark_data['film_id']


async def test_delete_bookmark(make_post_request, make_delete_request, make_get_request,
                               valid_token, unique_bookmark_data):
    create_response, _, _ = await make_post_request(
        BASE_BOOKMARKS_ENDPOINT,
        json=unique_bookmark_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    bookmark_id = create_response['id']

    _, _, del_status = await make_delete_request(
        f'{BASE_BOOKMARKS_ENDPOINT}/{bookmark_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert del_status == HTTPStatus.NO_CONTENT

    _, _, get_status = await make_get_request(
        f'{BASE_BOOKMARKS_ENDPOINT}/{bookmark_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert get_status == HTTPStatus.NOT_FOUND


async def test_get_bookmarks_by_user(
        make_post_request,
        make_get_request,
        token_factory,
        unique_bookmark_data
):
    test_user_id = 'user_test'
    user_token = token_factory(user_id=test_user_id)

    film_ids = []
    for i in range(3):
        data = deepcopy(unique_bookmark_data)
        data['film_id'] = f'film_{i}_{uuid.uuid4()}'
        film_ids.append(data['film_id'])
        _, _, status = await make_post_request(
            BASE_BOOKMARKS_ENDPOINT,
            json=data,
            headers={'Authorization': f'Bearer {user_token}'}
        )
        assert status == HTTPStatus.OK

    response_json, _, status = await make_get_request(
        f'{BASE_BOOKMARKS_ENDPOINT}/users/{test_user_id}',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert status == HTTPStatus.OK
    assert 'items' in response_json
    assert 'total' in response_json
    items = response_json['items']
    total = response_json['total']
    assert total == len(items)
    returned_film_ids = [item['film_id'] for item in items]
    for fid in film_ids:
        assert fid in returned_film_ids


async def test_search_bookmarks(make_post_request, valid_token, unique_bookmark_data):
    film_ids = []
    for i in range(3):
        data = deepcopy(unique_bookmark_data)
        data['film_id'] = f'search_film_{i}_{uuid.uuid4()}'
        film_ids.append(data['film_id'])
        _, _, status = await make_post_request(
            BASE_BOOKMARKS_ENDPOINT,
            json=data,
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert status == HTTPStatus.OK

    target_film_id = film_ids[1]
    search_payload = {
        'filters': {'film_id': target_film_id},
        'skip': 0,
        'limit': 10,
        'sort_by': None,
        'sort_order': 1
    }
    search_response, _, status = await make_post_request(
        f'{BASE_BOOKMARKS_ENDPOINT}/search',
        json=search_payload,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK
    assert 'items' in search_response
    assert 'total' in search_response
    items = search_response['items']
    total = search_response['total']
    assert total == 1
    assert len(items) == 1
    assert items[0]['film_id'] == target_film_id
