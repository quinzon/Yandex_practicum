import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.movies_data import es_movies_data


@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data):
    await es_write_data(es_movies_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)
    response = await make_get_request('/api/v1/films/search/', {'query': 'The Star'})

    assert response.status == 200
    body = await response.json()
    assert len(body) == 50
