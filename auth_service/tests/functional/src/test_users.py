import pytest
from http import HTTPStatus

from auth_service.tests.functional.testdata.authentication import valid_user, valid_login

pytestmark = pytest.mark.asyncio
ENDPOINT = '/api/v1/users'


# Test for getting user profile
async def test_get_profile(make_get_request, get_tokens):
    # Get valid tokens
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    # Send a request to get the profile
    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['email'] == valid_user['email']
    assert response_body['first_name'] == valid_user['first_name']
    assert response_body['last_name'] == valid_user['last_name']


# Test for updating user profile
async def test_update_profile(make_put_request, get_tokens):
    # Get valid tokens
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    # Prepare new profile data
    update_data = {
        'first_name': 'UpdatedName',
        'last_name': 'UpdatedLastName',
        'password': 'newStrongPassword123!'
    }

    # Send a request to update the profile
    response_body, headers, status = await make_put_request(
        f'{ENDPOINT}/profile',
        json=update_data,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['first_name'] == 'UpdatedName'
    assert response_body['last_name'] == 'UpdatedLastName'


# Test for getting login history
async def test_get_login_history(make_get_request, get_tokens):
    # Get valid tokens
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    # Send a request to get login history
    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile/login-history',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert len(response_body) > 0  # Ensure there is at least one entry in login history


# Test for invalid access token
async def test_get_profile_invalid_token(make_get_request):
    # Use an invalid token
    invalid_token = 'invalid_token'

    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile',
        headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert status == HTTPStatus.UNAUTHORIZED
