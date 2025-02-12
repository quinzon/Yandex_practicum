import uuid
from copy import deepcopy
from http import HTTPStatus

import pytest

from ugc_service.tests.functional.testdata.review_data import (
    review_create_data as base_review_create_data,
    review_update_data,
    search_request_data,
    reaction_request_data,
)

pytestmark = pytest.mark.asyncio

BASE_ENDPOINT = '/api/v1/ugc/reviews'


@pytest.fixture
def unique_review_create_data():
    data = deepcopy(base_review_create_data)
    data['film_id'] = str(uuid.uuid4())
    return data


async def test_create_review(make_post_request, valid_token, unique_review_create_data):
    response, headers, status = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert 'id' in response, 'Response does not contain "id"'
    assert response['user_id'] == unique_review_create_data['user_id']
    assert response['film_id'] == unique_review_create_data['film_id']


async def test_create_review_duplicate(make_post_request, valid_token, unique_review_create_data):
    response1, _, status1 = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status1 == HTTPStatus.OK, f'Expected {HTTPStatus.OK} on first creation, got {status1}'

    response2, _, status2 = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status2 == HTTPStatus.CONFLICT, f'Expected {HTTPStatus.CONFLICT} on duplicate creation, got {status2}'


async def test_search_reviews(make_post_request, valid_token, unique_review_create_data):
    create_response, _, _ = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    review_id = create_response['id']

    search_payload = deepcopy(search_request_data)
    search_payload['filters']['film_id'] = unique_review_create_data['film_id']

    response, _, status = await make_post_request(
        f'{BASE_ENDPOINT}/search',
        json=search_payload,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert 'items' in response, 'Response does not contain "items"'
    found = any(item['id'] == review_id for item in response['items'])
    assert found, f'Review with id={review_id} not found in search results'


async def test_get_review(make_get_request, make_post_request, valid_token,
                          unique_review_create_data):
    create_response, _, _ = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    review_id = create_response['id']

    response, _, status = await make_get_request(
        f'{BASE_ENDPOINT}/{review_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert response[
               'id'] == review_id, f'Returned ID ({response["id"]}) does not match expected ({review_id})'


async def test_update_review(make_put_request, make_post_request, valid_token,
                             unique_review_create_data):
    create_response, _, _ = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    review_id = create_response['id']

    response, _, status = await make_put_request(
        f'{BASE_ENDPOINT}/{review_id}',
        json=review_update_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert response['review_text'] == review_update_data[
        'review_text'], 'Review text was not updated correctly'
    assert response['rating'] == review_update_data[
        'rating'], 'Review rating was not updated correctly'


async def test_delete_review(make_delete_request, make_post_request, make_get_request, valid_token,
                             unique_review_create_data):
    create_response, _, _ = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    review_id = create_response['id']

    _, _, status = await make_delete_request(
        f'{BASE_ENDPOINT}/{review_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.NO_CONTENT, f'Expected {HTTPStatus.NO_CONTENT}, got {status}'

    _, _, status = await make_get_request(
        f'{BASE_ENDPOINT}/{review_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.NOT_FOUND, f'Expected {HTTPStatus.NOT_FOUND} after deletion, got {status}'


async def test_react_to_review(make_patch_request, make_post_request, valid_token,
                               unique_review_create_data):
    create_response, _, _ = await make_post_request(
        BASE_ENDPOINT,
        json=unique_review_create_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    review_id = create_response['id']

    _, _, status = await make_patch_request(
        f'{BASE_ENDPOINT}/{review_id}/reaction',
        json=reaction_request_data,
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.NO_CONTENT, f'Expected {HTTPStatus.NO_CONTENT}, got {status}'


async def test_get_reviews_by_user(make_get_request, make_post_request, valid_token,
                                   unique_review_create_data):
    test_user_id = 'user_for_test'
    unique_review_create_data['user_id'] = test_user_id

    created_review_ids = []
    for _ in range(3):
        response, _, status = await make_post_request(
            BASE_ENDPOINT,
            json=unique_review_create_data,
            headers={'Authorization': f'Bearer {valid_token}'}
        )
        assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
        created_review_ids.append(response['id'])

    response, _, status = await make_get_request(
        f'{BASE_ENDPOINT}/users/{test_user_id}',
        headers={'Authorization': f'Bearer {valid_token}'}
    )
    assert status == HTTPStatus.OK, f'Expected {HTTPStatus.OK}, got {status}'
    assert 'items' in response, 'Response must contain "items"'

    returned_ids = [item['id'] for item in response['items']]
    for review_id in created_review_ids:
        assert review_id in returned_ids, f'Review {review_id} not found in user reviews'
