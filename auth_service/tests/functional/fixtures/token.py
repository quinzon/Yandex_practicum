import pytest_asyncio


@pytest_asyncio.fixture
async def get_tokens(make_post_request):
    async def _get_tokens(email: str, password: str):
        login_data = {
            "email": email,
            "password": password
        }
        response_body, _, status = await make_post_request("/auth/login", json=login_data)
        assert status == 200
        return response_body["access_token"], response_body["refresh_token"]
    return _get_tokens


@pytest_asyncio.fixture
async def get_refresh_token(get_tokens):
    async def _get_refresh_token(email: str, password: str):
        _, refresh_token = await get_tokens(email, password)
        return refresh_token
    return _get_refresh_token
