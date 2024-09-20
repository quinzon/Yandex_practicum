import uuid
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings

ENDPOINT = '/api/v1/persons/'


# Tests for edge cases in UUID validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_id, expected_status", [
        ("invalid-uuid", HTTPStatus.UNPROCESSABLE_ENTITY),
        (str(uuid.uuid4()), HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_person_id_validation(make_get_request, person_id, expected_status):
    response, _, status = await make_get_request(f"{ENDPOINT}{person_id}")
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
async def test_person_list_pagination_validation(make_get_request, page_size, page_number, expected_status):
    params = {'page_size': page_size, 'page_number': page_number}
    _, _, status = await make_get_request(f"{ENDPOINT}", params=params)
    assert status == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data, expected_status", [
        ({'id': str(uuid.uuid4()), 'full_name': 'Test Person'}, HTTPStatus.OK),
        ({'id': str(uuid.uuid4()), 'full_name': 'Non-existent Person'}, HTTPStatus.INTERNAL_SERVER_ERROR)
    ]
)
async def test_get_person_by_id(make_get_request, es_write_data, person_data, expected_status):
    # If success is expected, load the data into Elasticsearch
    if expected_status == HTTPStatus.OK:
        await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}")
    assert status == expected_status

    if expected_status == HTTPStatus.OK:
        # Validate the successful response
        assert response['id'] == person_data['id']
        assert response['full_name'] == person_data['full_name']
    else:
        # Check the error message
        assert 'detail' in response
        assert 'NotFoundError' in response['detail']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data, film_data, expected_status", [
        (
                {'id': str(uuid.uuid4()), 'full_name': 'Test Person'},
                {'id': str(uuid.uuid4()), 'title': 'Test Film', 'imdb_rating': 8.0},
                HTTPStatus.OK
        ),
        (
                {'id': str(uuid.uuid4()), 'full_name': 'Non-existent Person'},
                None,
                HTTPStatus.OK
        )
    ]
)
async def test_get_person_films(make_get_request, es_write_data, person_data, film_data, expected_status):
    if expected_status == HTTPStatus.OK and film_data:
        # Load the person's data and their films into Elasticsearch
        await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)
        film_data['actors'] = [{'id': person_data['id'], 'full_name': person_data['full_name']}]
        await es_write_data([film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}/film")
    assert status == expected_status

    if film_data:
        assert len(response['items']) > 0
        assert response['items'][0]['title'] == film_data['title']
    else:
        assert len(response['items']) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data", [
        ({'id': str(uuid.uuid4()), 'full_name': 'Test Person'})
    ]
)
async def test_person_cache(make_get_request, es_write_data, es_client, person_data):
    # Write data to Elasticsearch
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # First API request to populate the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == person_data['id']

    # Delete the person's data from Elasticsearch
    await es_client.delete(index=test_settings.es_persons_index, id=person_data['id'])

    # The second API request should return data from the cache
    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}")
    assert status == HTTPStatus.OK
    assert response['id'] == person_data['id']


# Tests for the structure of the response for getting a person by ID
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data, expected_status", [
        ({'id': str(uuid.uuid4()), 'full_name': 'Test Person'}, HTTPStatus.OK),
    ]
)
async def test_person_by_id_response_structure(make_get_request, es_write_data, person_data, expected_status):
    # Add data to Elasticsearch
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # Request the person by ID
    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}")
    assert status == expected_status

    # Check the response structure
    assert 'id' in response
    assert 'full_name' in response
    assert 'films' in response
    assert isinstance(response['films'], list)


# Tests for the structure of the response for the list of persons with pagination
@pytest.mark.asyncio
async def test_persons_list_response_structure(make_get_request, es_write_data):
    person_data = {'id': str(uuid.uuid4()), 'full_name': 'Test Person'}
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # Request the list of persons
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
    for person in response['items']:
        assert 'id' in person
        assert 'full_name' in person


# Tests for the structure of the response for getting a person's films with pagination
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data, film_data, expected_status", [
        (
                {'id': str(uuid.uuid4()), 'full_name': 'Test Person'},
                {'id': str(uuid.uuid4()), 'title': 'Test Film', 'imdb_rating': 8.0},
                HTTPStatus.OK
        ),
    ]
)
async def test_person_films_response_structure(make_get_request, es_write_data, person_data, film_data,
                                               expected_status):
    # Load the person's data and their films into Elasticsearch
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)
    film_data['actors'] = [{'id': person_data['id'], 'full_name': person_data['full_name']}]
    await es_write_data([film_data], test_settings.es_movie_index, test_settings.es_movies_index_mapping)

    # Request the person's films
    response, _, status = await make_get_request(f"{ENDPOINT}{person_data['id']}/film")
    assert status == expected_status

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
    for film in response['items']:
        assert 'id' in film
        assert 'title' in film
        assert 'imdb_rating' in film


# Test basic search functionality
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, expected_results, expected_status", [
        ("John", 1, HTTPStatus.OK),
        ("Jane", 0, HTTPStatus.OK)  # No results found
    ]
)
async def test_search_persons(make_get_request, es_write_data, query, expected_results, expected_status):
    # Seed Elasticsearch with person data
    person_data = {'id': str(uuid.uuid4()), 'full_name': 'John Doe'}
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

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
    "persons_data, search_query, page_size, page_number, expected_total_items, expected_total_pages, expected_items_count",
    [
        ([
             {'id': str(uuid.uuid4()), 'full_name': 'John Doe'},
             {'id': str(uuid.uuid4()), 'full_name': 'Johnny Depp'},
             {'id': str(uuid.uuid4()), 'full_name': 'John Snow'}
         ], 'John', 2, 1, 2, 1, 2),
    ]
)
async def test_search_persons_pagination(make_get_request, es_write_data, persons_data, search_query, page_size,
                                         page_number, expected_total_items, expected_total_pages, expected_items_count):
    # Seed Elasticsearch with multiple persons
    await es_write_data(persons_data, test_settings.es_persons_index, test_settings.es_persons_index_mapping)

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
    "persons_data, expected_names", [
        ([
             {'id': str(uuid.uuid4()), 'full_name': 'John Doe'},
             {'id': str(uuid.uuid4()), 'full_name': 'Johanne Doe'},
             {'id': str(uuid.uuid4()), 'full_name': 'John Silverhand'},
             {'id': str(uuid.uuid4()), 'full_name': 'Jane Smith'}
         ], ['John Doe', 'John Silverhand']),  # Ascending order
    ]
)
async def test_search_persons_sort_ascending(make_get_request, es_write_data, persons_data, expected_names):
    # Seed Elasticsearch with multiple persons
    await es_write_data(persons_data, test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # Perform search with sorting by full_name in ascending order
    params = {'query': 'Joh', 'page_size': 10, 'page_number': 1, 'sort': 'full_name'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    items = response['items']
    names = [person['full_name'] for person in items]
    assert names == expected_names


# Test search with sorting desc
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "persons_data, expected_names", [
        ([
             {'id': str(uuid.uuid4()), 'full_name': 'John Doe'},
             {'id': str(uuid.uuid4()), 'full_name': 'Johanne Doe'},
             {'id': str(uuid.uuid4()), 'full_name': 'John Silverhand'},
             {'id': str(uuid.uuid4()), 'full_name': 'Jane Smith'}
         ], ['John Silverhand', 'John Doe']),  # Descending order
    ]
)
async def test_search_persons_sort_descending(make_get_request, es_write_data, persons_data, expected_names):
    # Seed Elasticsearch with multiple persons
    await es_write_data(persons_data, test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # Perform search with sorting by full_name in descending order
    params = {'query': 'John', 'page_size': 10, 'page_number': 1, 'sort': '-full_name'}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Verify sorting results
    items = response['items']
    names = [person['full_name'] for person in items]
    assert names == expected_names


# Test search with cache validation
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "person_data, search_query", [
        ({'id': str(uuid.uuid4()), 'full_name': 'John Doe'}, 'John')
    ]
)
async def test_search_persons_cache(make_get_request, es_write_data, es_client, person_data, search_query):
    # Insert data into Elasticsearch
    await es_write_data([person_data], test_settings.es_persons_index, test_settings.es_persons_index_mapping)

    # Perform initial search to cache the result
    params = {'query': search_query, 'page_size': 10, 'page_number': 1}
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK

    # Delete person data from Elasticsearch to check cache
    await es_client.delete(index=test_settings.es_persons_index, id=person_data['id'])

    # Perform search again and expect results from cache
    response, _, status = await make_get_request(f"{ENDPOINT}search", params=params)
    assert status == HTTPStatus.OK
    assert len(response['items']) == 1  # Cached result
    assert response['items'][0]['id'] == person_data['id']
