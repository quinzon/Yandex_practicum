import pytest
from http import HTTPStatus
from auth_service.tests.functional.testdata.authentication import (
    valid_user, valid_login, invalid_email_user, invalid_password_user,
    non_existent_user_login, wrong_password_login, invalid_refresh_token
)

ENDPOINT = '/api/v1/auth'
pytestmark = pytest.mark.asyncio


# Test user registration with valid data
async def test_register_user(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register', json=valid_user)

    assert status == HTTPStatus.CREATED
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body


# Test user registration with invalid email
async def test_register_user_with_invalid_email(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register', json=invalid_email_user)

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "detail" in response_body


# Test user registration with short password
async def test_register_user_with_invalid_password(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/register', json=invalid_password_user)

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "detail" in response_body


# Test login with valid data
async def test_login_user(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login', json=valid_login)

    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body


# Test login for a non-existent user
async def test_login_non_existent_user(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login', json=non_existent_user_login)

    assert status == HTTPStatus.UNAUTHORIZED
    assert "detail" in response_body


# Test login with incorrect password
async def test_login_with_wrong_password(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/login', json=wrong_password_login)

    assert status == HTTPStatus.UNAUTHORIZED
    assert "detail" in response_body


# Test token refresh with valid refresh_token
async def test_refresh_token(make_post_request, get_refresh_token):
    refresh_token = await get_refresh_token('test@example.com')

    refresh_data = {'token_value': refresh_token}

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh', json=refresh_data)

    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body


# Test token refresh with invalid refresh_token
async def test_refresh_token_invalid(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh', json=invalid_refresh_token)

    assert status == HTTPStatus.UNAUTHORIZED
    assert "detail" in response_body


# Test logout with valid refresh_token
async def test_logout_user(make_post_request, get_refresh_token):
    refresh_token = await get_refresh_token('test@example.com')

    logout_data = {'token_value': refresh_token}

    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data)

    assert status == HTTPStatus.OK
    assert response_body['message'] == 'Successfully logged out'


# Test logout with invalid refresh_token
async def test_logout_user_invalid_token(make_post_request):
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=invalid_refresh_token)

    assert status == HTTPStatus.UNAUTHORIZED
    assert "detail" in response_body


# Test double logout with the same token (blacklisted)
async def test_double_logout(make_post_request, get_refresh_token):
    refresh_token = await get_refresh_token('test@example.com')

    # First logout
    logout_data = {'token_value': refresh_token}
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data)
    assert status == HTTPStatus.OK
    assert response_body['message'] == 'Successfully logged out'

    # Attempt to logout with the same token (should be blacklisted)
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/logout', json=logout_data)
    assert status == HTTPStatus.UNAUTHORIZED
    assert response_body['detail'] == 'Invalid refresh token'


# Test reuse of refresh_token to obtain new tokens
async def test_double_use_refresh_token(make_post_request, get_refresh_token):
    refresh_token = await get_refresh_token('test@example.com')

    refresh_data = {'token_value': refresh_token}

    # First request for token refresh
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh', json=refresh_data)
    assert status == HTTPStatus.OK
    assert 'access_token' in response_body
    assert 'refresh_token' in response_body

    # Attempt to use the same refresh_token again (should be invalid)
    response_body, headers, status = await make_post_request(f'{ENDPOINT}/refresh', json=refresh_data)
    assert status == HTTPStatus.UNAUTHORIZED
    assert response_body['detail'] == 'Invalid refresh token'
