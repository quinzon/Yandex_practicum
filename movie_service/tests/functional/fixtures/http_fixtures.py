import aiohttp
import pytest_asyncio

from movie_service.tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def client_session():
    timeout = aiohttp.ClientTimeout(total=60)
    session = aiohttp.ClientSession(timeout=timeout)
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(client_session):
    async def inner(endpoint: str, params: dict = None):
        url = f'{test_settings.service_url}{endpoint}'
        async with client_session.get(url, params=params) as response:
            return await response.json(), response.headers, response.status

    return inner
