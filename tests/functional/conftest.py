import asyncio

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=f'{test_settings.es_host}:{test_settings.es_port}', verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(data: list[dict], index: str, mapping: dict):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        await es_client.indices.create(index=index, **mapping)

        if not await es_client.ping():
            raise Exception("Elasticsearch is not responding")

        updated, errors = await async_bulk(client=es_client, actions=data)

        if errors:
            raise Exception('Error occurred while writing data to Elasticsearch')

    return inner


@pytest_asyncio.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(client_session):
    async def inner(endpoint: str, params: dict):
        url = f'{test_settings.service_url}{endpoint}'
        async with client_session.get(url, params=params) as response:
            return response
    return inner
