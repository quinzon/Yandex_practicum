import http
from functools import lru_cache
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException, Depends

from src.models.film import Film
from src.models.person import PersonFilmsParticipant, Person
from src.services.base import SearchableApiServiceInterface
from src.services.cache import CacheService, get_cache_service
from src.services.film import FilmService, get_film_service
from src.services.request import RequestService, get_request_service


class PersonService(SearchableApiServiceInterface):

    def __init__(self, cache_service: CacheService, request_service: RequestService, film_service: FilmService):
        self.cache_service = cache_service
        self.request_service = request_service
        self.film_service = film_service

    async def get_by_id(self, person_id: UUID) -> PersonFilmsParticipant | None:
        """
        Get a person by their ID, including their films and roles.
        """
        cache_key = f"person:{person_id}"
        cached_data = await self.cache_service.get_from_cache_by_id(cache_key, PersonFilmsParticipant)
        if cached_data:
            return cached_data

        try:
            person = await self.request_service.response_by_id('persons', person_id, PersonFilmsParticipant)
            await self.cache_service.put_to_cache_by_id(cache_key, person)
            return person
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error occurred: {str(e)}")

    async def get_all(
            self,
            page_size: int = 10,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Person], int]:
        """
        Get a list of persons with pagination, sorting, and total count.
        """
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort)

    async def search(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Person], int]:
        """
        Search for persons based on a query string with pagination, sorting, and total count.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["full_name^3"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_persons(page_size, page_number, sort, search_body)

    async def get_person_films(
            self,
            person_id: UUID,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> tuple[List[Film], int]:
        """
        Get all films associated with a person by their ID, with pagination and sorting.
        """
        return await self.film_service.get_films_by_person_id(person_id, page_size, page_number, sort)

    async def _fetch_persons(
            self,
            page_size: int,
            page_number: int,
            sort: str | None = None,
            query: dict | None = None
    ) -> Tuple[List[Person], int]:
        """
        Helper method to fetch list of films with pagination, sorting, total count, and caching.
        """

        cache_key_parts = [f"persons:list:{page_number}:{page_size}:{sort}"]
        if query:
            cache_key_parts.append(str(query))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self.cache_service.get_list_from_cache(cache_key, Person)
        if cached_data:
            return cached_data

        try:
            persons, total_items = await self.request_service.response_list('persons', Person, page_size, page_number, sort, query)
            await self.cache_service.put_list_to_cache(cache_key, persons, total_items)

            return persons, total_items
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error: {str(e)}")


@lru_cache()
def get_person_service(
        cache_service: CacheService = Depends(get_cache_service),
        request_service: RequestService = Depends(get_request_service),
        film_service: FilmService = Depends(get_film_service)
) -> PersonService:
    return PersonService(cache_service, request_service, film_service)
