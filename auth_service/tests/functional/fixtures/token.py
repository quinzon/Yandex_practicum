from http import HTTPStatus

import pytest_asyncio


@pytest_asyncio.fixture(scope='function')
async def get_tokens(make_post_request):
    async def _get_tokens(email: str, password: str):
        login_data = {
            'email': email,
            'password': password
        }
        response_body, _, status = await make_post_request('/api/v1/auth/login', json=login_data)
        assert status == HTTPStatus.OK
        return response_body['access_token'], response_body['refresh_token']
    return _get_tokens
