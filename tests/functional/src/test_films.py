import uuid
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.movies_data import es_film_data, es_films_data

ENDPOINT = '/api/v1/films/'


# Tests for edge cases in UUID validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_id, expected_status", [
        ("invalid-uuid", HTTPStatus.UNPROCESSABLE_ENTITY),
        (str(uuid.uuid4()), HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_film_id_validation(make_get_request, film_id, expected_status):
    response, _, status = await make_get_request(f"{ENDPOINT}{film_id}")
    assert status == expected_status


# Tests for edge cases in pagination
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page_size, page_number, expected_status", [
        (0, 1, HTTPStatus.UNPROCESSABLE_ENTITY),  # Page size of zero
        (50, 0, HTTPStatus.UNPROCESSABLE_ENTITY),  # Page number of zero
        (50, -1, HTTPStatus.UNPROCESSABLE_ENTITY)  # Negative page number
    ]
)
async def test_film_list_pagination_validation(make_get_request, page_size, page_number, expected_status):
    params = {'page_size': page_size, 'page_number': page_number}
    _, _, status = await make_get_request(f"{ENDPOINT}", params=params)
    assert status == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_data, expected_status", [
        ({'id': str(uuid.uuid4()), 'title': 'Test Film title', 'imdb_rating': 5}, HTTPStatus.OK),
        ({'id': str(uuid.uuid4())}, HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_get_film_by_id(make_get_request, es_write_data, film_data, expected_status):
    # If success is expected, load the data into Elasticsearch
    if expected_status == HTTPStatus.OK:
        await es_write_data([film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    response, _, status = await make_get_request(f"{ENDPOINT}{film_data['id']}")
    assert status == expected_status

    if expected_status == HTTPStatus.OK:
        # Validate the successful response
        assert response['id'] == film_data['id']
        assert response['title'] == film_data['title']
        assert response['imdb_rating'] == film_data['imdb_rating']
    else:
        # Check the error message
        assert 'detail' in response
        assert 'NotFoundError' in response['detail']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_data", [
        ({'id': es_film_data['id']})
    ]
)
async def test_film_cache(make_get_request, es_write_data, es_client, film_data):
    # Write data to Elasticsearch
    await es_write_data([es_film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # First API request to populate the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{film_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == film_data['id']

    # Delete the film's data from Elasticsearch
    await es_client.delete(index=test_settings.es_movie_index, id=film_data['id'])

    # The second API request should return data from the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{film_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == film_data['id']


# Tests for the structure of the response for getting a film by ID
@pytest.mark.asyncio
async def test_film_by_id_response_structure(make_get_request, es_write_data):
    # Add data to Elasticsearch
    await es_write_data([es_film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Request the film by ID
    response, _, status = await make_get_request(f"{ENDPOINT}{es_film_data['id']}")
    assert status == HTTPStatus.OK

    # Check the response structure
    assert response == es_film_data


# Tests for the structure of the response for the list of films with pagination
@pytest.mark.asyncio
async def test_films_list_response_structure(make_get_request, es_write_data):
    await es_write_data(es_films_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Request the list of films
    params = {'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f"{ENDPOINT}", params=params)
    assert status == HTTPStatus.OK

    # Check the response structure
    assert 'meta' in response
    assert 'items' in response

    # Validate the meta structure
    meta = response['meta']
    assert 'page_size' in meta
    assert 'page_number' in meta
    assert 'total_items' in meta
    assert 'total_pages' in meta
    assert isinstance(meta['page_size'], int)
    assert isinstance(meta['page_number'], int)
    assert isinstance(meta['total_items'], int)
    assert isinstance(meta['total_pages'], int)

    # Validate the items structure
    assert isinstance(response['items'], list)
    for response_film, expected_film in zip(response['items'], es_films_data):
        assert response_film == expected_film


# Test basic search functionality
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, expected_results", [
        ("Man", 1),
        ("Woman", 0)
    ]
)
async def test_search_films(make_get_request, es_write_data, query, expected_results):
    # Seed Elasticsearch with film data
    film_data = {'id': str(uuid.uuid4()), 'title': 'Man who build the world', 'imdb_rating': 5}
    await es_write_data([film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Perform the search
    params = {'query': query, 'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f'{ENDPOINT}search', params=params)
    assert status == HTTPStatus.OK

    assert 'meta' in response
    assert 'items' in response
    assert len(response['items']) == expected_results


# Test search with pagination
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "films_data, search_query, page_size, page_number, expected_total_items, expected_total_pages, expected_items_count",
    [
        ([
             {'id': str(uuid.uuid4()), 'title': 'Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'V-Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'Manufacture', 'imdb_rating': 5}
         ], 'Man', 2, 1, 2, 1, 2),
    ]
)
async def test_search_films_pagination_validation(make_get_request, es_write_data, films_data, search_query,
                                                  page_size,
                                                  page_number, expected_total_items, expected_total_pages,
                                                  expected_items_count):
    # Seed Elasticsearch with multiple films
    await es_write_data(films_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Perform search with pagination
    params = {'query': search_query, 'page_size': page_size, 'page_number': page_number}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify pagination structure
    assert 'meta' in response
    assert 'items' in response
    assert len(response['items']) == expected_items_count

    meta = response['meta']
    assert meta['page_size'] == page_size
    assert meta['page_number'] == page_number
    assert meta['total_items'] == expected_total_items
    assert meta['total_pages'] == expected_total_pages


# Test search with sorting asc
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "films_data, expected_titles", [
        ([
             {'id': str(uuid.uuid4()), 'title': 'Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'V-Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'Manufacture', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'Main', 'imdb_rating': 5},
         ], ['Main', 'Man', 'V-Man']),  # Ascending order
    ]
)
async def test_search_films_sort_ascending(make_get_request, es_write_data, films_data, expected_titles):
    # Seed Elasticsearch with multiple films
    await es_write_data(films_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Perform search with sorting by title in ascending order
    params = {'query': 'Man', 'page_size': 10, 'page_number': 1, 'sort': 'title'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    films = response['items']
    titles = [film['title'] for film in films]
    assert titles == expected_titles


# Test search with sorting desc
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "films_data, expected_titles", [
        ([
             {'id': str(uuid.uuid4()), 'title': 'Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'V-Man', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'Manufacture', 'imdb_rating': 5},
             {'id': str(uuid.uuid4()), 'title': 'Main', 'imdb_rating': 5},
         ], ['V-Man', 'Man', 'Main']),  # Descending order
    ]
)
async def test_search_films_sort_descending(make_get_request, es_write_data, films_data, expected_titles):
    # Seed Elasticsearch with multiple films
    await es_write_data(films_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Perform search with sorting by title in descending order
    params = {'query': 'Man', 'page_size': 10, 'page_number': 1, 'sort': '-title'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    films = response['items']
    titles = [film['title'] for film in films]
    assert titles == expected_titles


# Test search with cache validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_data, search_query", [
        ({'id': str(uuid.uuid4()), 'title': 'Main', 'imdb_rating': 5}, 'Man')
    ]
)
async def test_search_films_cache(make_get_request, es_write_data, es_client, film_data, search_query):
    # Insert data into Elasticsearch
    await es_write_data([film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Perform initial search to cache the result
    params = {'query': search_query, 'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Delete film data from Elasticsearch to check cache
    await es_client.delete(index=test_settings.es_movie_index, id=film_data['id'])

    # Perform search again and expect results from cache
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK
    assert len(response['items']) == 1  # Cached result
    assert response['items'][0]['id'] == film_data['id']
