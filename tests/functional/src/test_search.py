import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.movies_data import es_movies_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star'},
                {'status': 200, 'length': 50}
        ),
        (
                {'query': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, expected_answer, query_data):
    await es_write_data(es_movies_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)
    body, headers, status = await make_get_request('/api/v1/films/search/', query_data)

    assert status == expected_answer.get('status')

    assert len(body['items']) == expected_answer.get('length')
