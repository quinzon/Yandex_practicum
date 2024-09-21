import uuid
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings

ENDPOINT = '/api/v1/genres/'


# Tests for edge cases in UUID validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_id, expected_status", [
        ("invalid-uuid", HTTPStatus.UNPROCESSABLE_ENTITY),
        (str(uuid.uuid4()), HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_genre_id_validation(make_get_request, genre_id, expected_status):
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_id}")
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
async def test_genre_list_pagination_validation(make_get_request, page_size, page_number, expected_status):
    params = {'page_size': page_size, 'page_number': page_number}
    _, _, status = await make_get_request(f"{ENDPOINT}", params=params)
    assert status == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data, expected_status", [
        ({'id': str(uuid.uuid4()), 'name': 'Action'}, HTTPStatus.OK),
        ({'id': str(uuid.uuid4()), 'name': 'Non-existent Genre'}, HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_get_genre_by_id(make_get_request, es_write_data, genre_data, expected_status):
    # If success is expected, load the data into Elasticsearch
    if expected_status == HTTPStatus.OK:
        await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}")
    assert status == expected_status

    if expected_status == HTTPStatus.OK:
        # Validate the successful response
        assert response['id'] == genre_data['id']
        assert response['name'] == genre_data['name']
    else:
        # Check the error message
        assert 'detail' in response
        assert 'NotFoundError' in response['detail']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data", [
        ({'id': str(uuid.uuid4()), 'name': 'Action'})
    ]
)
async def test_genre_cache(make_get_request, es_write_data, es_client, genre_data):
    # Write data to Elasticsearch
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # First API request to populate the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == genre_data['id']

    # Delete the genre's data from Elasticsearch
    await es_client.delete(index=test_settings.es_genre_index, id=genre_data['id'])

    # The second API request should return data from the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == genre_data['id']


# Tests for the structure of the response for getting a genre by ID
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data, expected_status", [
        ({'id': str(uuid.uuid4()), 'name': 'Action'}, HTTPStatus.OK),
    ]
)
async def test_genre_by_id_response_structure(make_get_request, es_write_data, genre_data, expected_status):
    # Add data to Elasticsearch
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Request the genre by ID
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}")
    assert status == expected_status

    # Check the response structure
    assert 'id' in response
    assert 'name' in response


# Tests for the structure of the response for the list of genres with pagination
@pytest.mark.asyncio
async def test_genres_list_response_structure(make_get_request, es_write_data):
    genre_data = {'id': str(uuid.uuid4()), 'name': 'Action'}
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Request the list of genres
    params = {'page_size': 1, 'page_number': 1}
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
    for genre in response['items']:
        assert 'id' in genre
        assert 'name' in genre


# Test basic search functionality
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, expected_results, expected_status", [
        ("Action", 1, HTTPStatus.OK),
        ("Comedy", 0, HTTPStatus.OK)  # No results found
    ]
)
async def test_search_genres(make_get_request, es_write_data, query, expected_results, expected_status):
    # Seed Elasticsearch with genre data
    genre_data = {'id': str(uuid.uuid4()), 'name': 'Action'}
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Perform the search
    params = {'query': query, 'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == expected_status

    if status == HTTPStatus.OK:
        assert 'meta' in response
        assert 'items' in response
        assert len(response['items']) == expected_results


# Test search with pagination
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genres_data, search_query, page_size, page_number, expected_total_items, expected_total_pages, expected_items_count",
    [
        ([
             {'id': str(uuid.uuid4()), 'name': 'Action'},
             {'id': str(uuid.uuid4()), 'name': 'Adventure'},
             {'id': str(uuid.uuid4()), 'name': 'Animation'}
         ], 'Action', 1, 1, 1, 1, 1),
    ]
)
async def test_search_genres_pagination(make_get_request, es_write_data, genres_data, search_query, page_size,
                                        page_number, expected_total_items, expected_total_pages, expected_items_count):
    # Seed Elasticsearch with multiple genres
    await es_write_data(genres_data, test_settings.es_genre_index, test_settings.es_genres_index_mapping)

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
    "genres_data, expected_names", [
        ([
             {'id': str(uuid.uuid4()), 'name': 'Action Adventure'},
             {'id': str(uuid.uuid4()), 'name': 'Action Comedy'},
             {'id': str(uuid.uuid4()), 'name': 'Action Thriller'},
             {'id': str(uuid.uuid4()), 'name': 'Comedy'}
         ], ['Action Adventure', 'Action Comedy', 'Action Thriller']),  # Ascending order
    ]
)
async def test_search_genres_sort_ascending(make_get_request, es_write_data, genres_data, expected_names):
    # Seed Elasticsearch with multiple genres
    await es_write_data(genres_data, test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Perform search with sorting by name in ascending order
    params = {'query': 'Action', 'page_size': 10, 'page_number': 1, 'sort': 'name'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    items = response['items']
    names = [genre['name'] for genre in items]
    assert names == expected_names


# Test search with sorting desc
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genres_data, expected_names", [
        ([
             {'id': str(uuid.uuid4()), 'name': 'Action Adventure'},
             {'id': str(uuid.uuid4()), 'name': 'Action Comedy'},
             {'id': str(uuid.uuid4()), 'name': 'Action Thriller'},
             {'id': str(uuid.uuid4()), 'name': 'Comedy'}
         ], ['Action Thriller', 'Action Comedy', 'Action Adventure']),  # Descending order
    ]
)
async def test_search_genres_sort_descending(make_get_request, es_write_data, genres_data, expected_names):
    # Seed Elasticsearch with multiple genres
    await es_write_data(genres_data, test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Perform search with sorting by name in descending order
    params = {'query': 'Action', 'page_size': 10, 'page_number': 1, 'sort': '-name'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    items = response['items']
    names = [genre['name'] for genre in items]
    assert names == expected_names


# Test search with cache validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data, search_query", [
        ({'id': str(uuid.uuid4()), 'name': 'Action'}, 'Action')
    ]
)
async def test_search_genres_cache(make_get_request, es_write_data, es_client, genre_data, search_query):
    # Insert data into Elasticsearch
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Perform initial search to cache the result
    params = {'query': search_query, 'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Delete genre data from Elasticsearch to check cache
    await es_client.delete(index=test_settings.es_genre_index, id=genre_data['id'])

    # Perform search again and expect results from cache
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK
    assert len(response['items']) == 1  # Cached result
    assert response['items'][0]['id'] == genre_data['id']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data, films_data, expected_status, expected_films", [
        (
            {'id': str(uuid.uuid4()), 'name': 'Action'},
            [
                {'id': str(uuid.uuid4()), 'title': 'Film A', 'imdb_rating': 8.0, 'genres': [{'id': 'genre_id', 'name': 'Action'}]},
                {'id': str(uuid.uuid4()), 'title': 'Film B', 'imdb_rating': 7.5, 'genres': [{'id': 'genre_id', 'name': 'Action'}]},
            ],
            HTTPStatus.OK,
            ['Film A', 'Film B']
        ),
    ]
)
async def test_get_genre_films_success(make_get_request, es_write_data, genre_data, films_data, expected_status, expected_films):
    # Prepare genre data in Elasticsearch
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Prepare film data linked to this genre
    for film in films_data:
        film['genres'][0]['id'] = genre_data['id']
    await es_write_data(films_data, test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Execute request to get films by genre
    params = {'page_size': 50, 'page_number': 1, 'sort': '-imdb_rating'}
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}/film/", params=params)
    assert status == expected_status

    # Check that the correct films are returned
    items = response['items']
    titles = [film['title'] for film in items]
    assert titles == expected_films

    # Check the pagination metadata structure
    assert 'meta' in response
    meta = response['meta']
    assert meta['page_size'] == 50
    assert meta['page_number'] == 1
    assert isinstance(meta['total_items'], int)
    assert isinstance(meta['total_pages'], int)


# Test for case when genre exists but there are no films
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre_data, expected_status", [
        (
            {'id': str(uuid.uuid4()), 'name': 'Comedy'},
            HTTPStatus.OK
        ),
    ]
)
async def test_get_genre_films_no_films(make_get_request, es_write_data, genre_data, expected_status):
    # Prepare genre data in Elasticsearch
    await es_write_data([genre_data], test_settings.es_genre_index, test_settings.es_genres_index_mapping)

    # Execute request to get films by genre
    params = {'page_size': 50, 'page_number': 1, 'sort': '-imdb_rating'}
    response, _, status = await make_get_request(f"{ENDPOINT}{genre_data['id']}/film/", params=params)
    assert status == expected_status

    # Check that no films are returned
    items = response['items']
    assert len(items) == 0

    # Check the pagination metadata structure
    assert 'meta' in response
    meta = response['meta']
    assert meta['page_size'] == 50
    assert meta['page_number'] == 1
    assert meta['total_items'] == 0
    assert meta['total_pages'] == 0


# Test for invalid UUID genre ID
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_genre_id, expected_status", [
        ('invalid-uuid', HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
async def test_get_genre_films_invalid_uuid(make_get_request, invalid_genre_id, expected_status):
    # Execute request to get films by invalid UUID genre ID
    params = {'page_size': 50, 'page_number': 1, 'sort': '-imdb_rating'}
    _, _, status = await make_get_request(f"{ENDPOINT}{invalid_genre_id}/film/", params=params)
    assert status == expected_status
