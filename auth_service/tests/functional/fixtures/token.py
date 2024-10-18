from http import HTTPStatus

import pytest_asyncio

from auth_service.tests.functional.testdata.authentication import valid_user


@pytest_asyncio.fixture(scope='function')
async def create_user(make_post_request):
    response_body, _, status = await make_post_request('/api/v1/auth/register', json=valid_user)
    assert status == HTTPStatus.OK
    return response_body


@pytest_asyncio.fixture(scope='function')
async def get_tokens(create_user, make_post_request):
    async def _get_tokens(email: str, password: str):
        login_data = {
            'email': email,
            'password': password
        }
        response_body, _, status = await make_post_request('/api/v1/auth/login', json=login_data)
        assert status == HTTPStatus.OK
        return response_body['access_token'], response_body['refresh_token']
    return _get_tokens
