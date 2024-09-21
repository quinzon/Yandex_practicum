import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


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

        bulk_data = []
        for doc in data:
            bulk_data.append({
                '_index': index,
                '_id': doc['id'],
                '_source': doc
            })
        updated, errors = await async_bulk(client=es_client, actions=bulk_data)

        await es_client.indices.refresh(index=index)

        if errors:
            raise Exception('Error occurred while writing data to Elasticsearch')

    return inner
