import uuid

import aiohttp
import pytest_asyncio

from auth_service.tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def client_session():
    timeout = aiohttp.ClientTimeout(total=60)
    session = aiohttp.ClientSession(timeout=timeout)
    yield session
    await session.close()


def prepare_headers(headers: dict = dict()) -> dict:
    if headers is None:
        headers = {}
    headers['x-request-id'] = str(uuid.uuid4())
    return headers


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(client_session):
    async def inner(endpoint: str, params: dict = dict(), headers: dict = dict()):
        url = f'{test_settings.service_url}{endpoint}'
        headers = prepare_headers(headers)
        async with client_session.get(url, params=params, headers=headers) as response:
            return await response.json(), response.headers, response.status
    return inner


@pytest_asyncio.fixture(name='make_post_request')
async def make_post_request(client_session):
    async def inner(endpoint: str, json: dict = dict(), headers: dict = dict()):
        url = f'{test_settings.service_url}{endpoint}'
        headers = prepare_headers(headers)
        async with client_session.post(url, json=json, headers=headers) as response:
            response_body = await response.json()
            return response_body, response.headers, response.status
    return inner


@pytest_asyncio.fixture(name='make_put_request')
async def make_put_request(client_session):
    async def inner(endpoint: str, json=None, headers=None):
        url = f'{test_settings.service_url}{endpoint}'
        headers = prepare_headers(headers)
        async with client_session.put(url, json=json, headers=headers) as response:
            return await response.json(), response.headers, response.status
    return inner


@pytest_asyncio.fixture(name='make_delete_request')
async def make_delete_request(client_session):
    async def inner(endpoint: str, headers: dict = dict()):
        url = f'{test_settings.service_url}{endpoint}'
        headers = prepare_headers(headers)
        async with client_session.delete(url, headers=headers) as response:
            return await response.json(), response.headers, response.status
    return inner
