# flake8: noqa
import uuid
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus

import pytest

from ugc_service.tests.functional.fixtures.common import unique_rating_create_data

pytestmark = pytest.mark.asyncio

BASE_RATINGS_ENDPOINT = '/api/v1/ugc/ratings'


async def test_create_rating(make_post_request, valid_token, unique_rating_create_data):
    response_json, _, status = await make_post_request(
        BASE_RATINGS_ENDPOINT,
        json=unique_rating_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'

    assert 'user_id' in response_json, 'Missing "user_id" in response'
    assert 'film_id' in response_json, 'Missing "film_id" in response'
    assert 'rating' in response_json, 'Missing "rating" in response'
    assert 'timestamp' in response_json, 'Missing "timestamp" in response'

    assert response_json['user_id'] == unique_rating_create_data['user_id']
    assert response_json['film_id'] == unique_rating_create_data['film_id']
    assert response_json['rating'] == unique_rating_create_data['rating']

    try:
        datetime.fromisoformat(response_json['timestamp'].replace('Z', ''))
    except ValueError:
        pytest.fail('timestamp is not a valid ISO datetime string')


async def test_create_rating_duplicate(make_post_request, valid_token, unique_rating_create_data):
    _, _, status1 = await make_post_request(
        BASE_RATINGS_ENDPOINT,
        json=unique_rating_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status1 == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status1}'

    _, _, status2 = await make_post_request(
        BASE_RATINGS_ENDPOINT,
        json=unique_rating_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status2 == HTTPStatus.CONFLICT, f'Expected {HTTPStatus.CONFLICT}, got {status2}'


async def test_get_rating_by_id(make_post_request, make_get_request, valid_token,
                                unique_rating_create_data):
    create_response, _, _ = await make_post_request(
        BASE_RATINGS_ENDPOINT,
        json=unique_rating_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    rating_id = create_response['id']

    response_json, _, status = await make_get_request(
        f'{BASE_RATINGS_ENDPOINT}/{rating_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert response_json['film_id'] == unique_rating_create_data['film_id']


async def test_delete_rating(
        make_post_request, make_delete_request, make_get_request,
        valid_token, unique_rating_create_data
):
    create_response, _, _ = await make_post_request(
        BASE_RATINGS_ENDPOINT,
        json=unique_rating_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    rating_id = create_response['id']

    _, _, del_status = await make_delete_request(
        f'{BASE_RATINGS_ENDPOINT}/{rating_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert del_status == HTTPStatus.NO_CONTENT, f'Expected {HTTPStatus.NO_CONTENT}, got {del_status}'

    _, _, get_status = await make_get_request(
        f'{BASE_RATINGS_ENDPOINT}/{rating_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert get_status == HTTPStatus.NOT_FOUND, f'Expected {HTTPStatus.NOT_FOUND}, got {get_status}'


async def test_get_average_rating(make_post_request, make_get_request, valid_token,
                                  unique_rating_create_data):
    film_id = f'film_{uuid.uuid4()}'
    values = [3, 7, 9]
    user_ids = [f'user_{uuid.uuid4()}' for _ in values]

    for user_id, rating_val in zip(user_ids, values):
        rating_data = deepcopy(unique_rating_create_data)
        rating_data['film_id'] = film_id
        rating_data['user_id'] = user_id
        rating_data['rating'] = rating_val

        _, _, status = await make_post_request(
            BASE_RATINGS_ENDPOINT,
            json=rating_data,
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'

    response_json, _, status = await make_get_request(
        f'{BASE_RATINGS_ENDPOINT}/{film_id}/average',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'

    assert 'film_id' in response_json, 'Missing "film_id"'
    assert 'avg_rating' in response_json, 'Missing "avg_rating"'
    assert 'total_ratings' in response_json, 'Missing "total_ratings"'

    expected_avg = sum(values) / len(values)
    actual_avg = response_json['avg_rating']
    assert abs(actual_avg - expected_avg) < 1e-6, (
        f'Expected avg_rating={expected_avg}, got {actual_avg}'
    )
    assert response_json['total_ratings'] == len(values), (
        f'Expected total_ratings={len(values)}, got {response_json["total_ratings"]}'
    )

    assert response_json['film_id'] == film_id, (
        f'Expected film_id={film_id}, got {response_json["film_id"]}'
    )


async def test_get_ratings_by_user(make_post_request, make_get_request, valid_token,
                                   unique_rating_create_data):
    test_user_id = f'user_{uuid.uuid4()}'
    rating_values = [1, 5, 10]
    created_film_ids = []

    for val in rating_values:
        data = deepcopy(unique_rating_create_data)
        data['user_id'] = test_user_id
        data['rating'] = val
        data['film_id'] = f'film_{uuid.uuid4()}'
        created_film_ids.append(data['film_id'])

        _, _, status = await make_post_request(
            BASE_RATINGS_ENDPOINT,
            json=data,
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'

    response_json, _, status = await make_get_request(
        f'{BASE_RATINGS_ENDPOINT}/users/{test_user_id}?sort_by=rating',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'

    assert 'total' in response_json, 'Missing "total" in response'
    assert 'items' in response_json, 'Missing "items" in response'

    items = response_json['items']
    total = response_json['total']
    assert isinstance(items, list), 'items must be a list'
    assert total == len(items), (
        f'Expected total={len(items)}, got {total}'
    )

    film_ids_in_response = [item['film_id'] for item in items]
    for fid in created_film_ids:
        assert fid in film_ids_in_response, (
            f'Missing film_id={fid} in items response'
        )

    for item, expected_val in zip(items, rating_values):
        assert item['user_id'] == test_user_id, (
            f'Expected user_id={test_user_id}, got {item["user_id"]}'
        )
        assert item['rating'] == expected_val, (
            f'Expected rating={expected_val}, got {item["rating"]}'
        )
        assert 'timestamp' in item, 'Missing "timestamp" in item'

        try:
            datetime.fromisoformat(item['timestamp'].replace('Z', ''))
        except ValueError:
            pytest.fail('timestamp is not a valid ISO datetime string')
