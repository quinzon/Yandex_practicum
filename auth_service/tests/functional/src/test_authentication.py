from http import HTTPStatus

import pytest

from auth_service.tests.functional.testdata.authentication import (
    valid_login, valid_user, invalid_email_user, invalid_password_user, non_existent_user_login,
    wrong_password_login, invalid_refresh_token
)

ENDPOINT = '/api/v1/auth'
pytestmark = pytest.mark.asyncio


# Test user registration with valid data
async def test_register_user(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register',
                                                             json=valid_user)

    assert status == HTTPStatus.OK
    assert 'email' in response_body
    assert 'id' in response_body


# Test user registration with invalid email
async def test_register_user_with_invalid_email(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register',
                                                             json=invalid_email_user)

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'detail' in response_body


# Test user registration with short password
async def test_register_user_with_invalid_password(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register',
                                                             json=invalid_password_user)

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'detail' in response_body


# Test login with valid data
async def test_login_user(make_post_request, create_user):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login', json=valid_login)

    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body


# Test login for a non-existent user
async def test_login_non_existent_user(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login',
                                                             json=non_existent_user_login)

    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response_body


# Test login with incorrect password
async def test_login_with_wrong_password(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login',
                                                             json=wrong_password_login)

    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response_body


# Test token refresh with valid refresh_token
async def test_refresh_token(make_post_request, get_tokens):
    access_token, refresh_token = await get_tokens(valid_login['email'], valid_login['password'])

    headers = {'Authorization': f'Bearer {access_token}'}
    refresh_data = {'refresh_token': refresh_token}

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh',
                                                             json=refresh_data, headers=headers)

    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body


# Test token refresh with invalid refresh_token
async def test_refresh_token_invalid(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh',
                                                             json=invalid_refresh_token)

    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response_body


# Test logout with valid refresh_token
async def test_logout_user(make_post_request, get_tokens):
    access_token, refresh_token = await get_tokens(valid_login['email'], valid_login['password'])

    headers = {'Authorization': f'Bearer {access_token}'}
    logout_data = {'refresh_token': refresh_token}

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data,
                                                             headers=headers)

    assert status == HTTPStatus.OK


# Test logout with invalid refresh_token
async def test_logout_user_invalid_token(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout',
                                                             json=invalid_refresh_token)

    assert status == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response_body


# Test double logout with the same token (blacklisted)
async def test_double_logout(make_post_request, get_tokens):
    access_token, refresh_token = await get_tokens(valid_login['email'], valid_login['password'])

    request_headers = {'Authorization': f'Bearer {access_token}'}
    logout_data = {'refresh_token': refresh_token}

    # First logout
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data,
                                                             headers=request_headers)
    assert status == HTTPStatus.OK

    # Second logout
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data,
                                                             headers=request_headers)
    assert status == HTTPStatus.UNAUTHORIZED


# Test reuse of refresh_token to obtain new tokens
async def test_double_use_refresh_token(make_post_request, get_tokens):
    access_token, refresh_token = await get_tokens(valid_login['email'], valid_login['password'])

    request_headers = {'Authorization': f'Bearer {access_token}'}
    refresh_data = {'refresh_token': refresh_token}

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh',
                                                             json=refresh_data,
                                                             headers=request_headers)

    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh',
                                                             json=refresh_data,
                                                             headers=request_headers)
    assert status == HTTPStatus.UNAUTHORIZED
