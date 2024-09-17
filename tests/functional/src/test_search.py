import datetime
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_search():
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [
            {'id': str(uuid.uuid4()), 'name': 'Action'},
            {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors': [
            {'id': str(uuid.uuid4()), 'full_name': 'Stan'}
        ],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': str(uuid.uuid4()), 'full_name': 'Ann'},
            {'id': str(uuid.uuid4()), 'full_name': 'Bob'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'full_name': 'Ben'},
            {'id': str(uuid.uuid4()), 'full_name': 'Howard'}
        ],
    } for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    es_client = AsyncElasticsearch(hosts=f'{test_settings.es_host}:{test_settings.es_port}', verify_certs=False)
    if await es_client.indices.exists(index=test_settings.es_movie_index):
        await es_client.indices.delete(index=test_settings.es_movie_index)
    await es_client.indices.create(index=test_settings.es_movie_index, **test_settings.es_movies_index_mapping)

    if not await es_client.ping():
        raise Exception("Elasticsearch не отвечает")

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    await es_client.close()

    if errors:
        for error in errors:
            print(f"Bulk indexing error: {error}")
        raise Exception('Ошибка записи данных в Elasticsearch')

    async with aiohttp.ClientSession() as session:
        url = test_settings.service_url + '/api/v1/films/search/'
        query_data = {'query': 'The Star'}
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

    assert status == 200
    assert len(body) == 50
