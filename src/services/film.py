import http
from functools import lru_cache
from typing import List, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException

from src.models.film import FilmDetail, Film
from src.services.base import SearchableApiServiceInterface
from src.services.cache import CacheService, get_cache_service
from src.services.request import RequestService, get_request_service


class FilmService(SearchableApiServiceInterface):

    def __init__(self, cache_service: CacheService, request_service: RequestService):
        self.cache_service = cache_service
        self.request_service = request_service

    async def get_by_id(self, film_id: UUID) -> FilmDetail | None:
        """
        Retrieve a film by its unique ID.
        """
        cache_key = f"film:{film_id}"
        cached_data = await self.cache_service.get_from_cache_by_id(cache_key, FilmDetail)
        if cached_data:
            return cached_data

        try:
            film = await self.request_service.response_by_id('movies', film_id, FilmDetail)
            await self.cache_service.put_to_cache_by_id(cache_key, film)
            return film
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error occurred: {str(e)}")

    async def get_films_by_person_id(
            self,
            person_id: UUID,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Film], int]:
        """
        Fetch all films where a person (by person_id) appears in any role: actor, writer, or director.
        Support pagination and sorting.
        """
        query = {
            "bool": {
                "should": [
                    {"nested": {
                        "path": "actors",
                        "query": {
                            "term": {"actors.id": str(person_id)}
                        }
                    }},
                    {"nested": {
                        "path": "writers",
                        "query": {
                            "term": {"writers.id": str(person_id)}
                        }
                    }},
                    {"nested": {
                        "path": "directors",
                        "query": {
                            "term": {"directors.id": str(person_id)}
                        }
                    }}
                ]
            }
        }

        try:
            films, total_items = await self.request_service.response_list('movies', Film, page_size, page_number, sort, query)
            return films, total_items
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error fetching films for person: {str(e)}")

    async def get_films_by_genre_id(
            self,
            genre_id: UUID,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Film], int]:
        """
        Fetch all films where the genre matches genre_id.
        Support pagination and sorting.
        """
        query = {
            "nested": {
                "path": "genres",
                "query": {
                    "term": {"genres.id": str(genre_id)}
                }
            }
        }
        return await self._fetch_films(page_size, page_number, sort, query)

    async def get_all(
            self,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[FilmDetail], int]:
        """
        Get a list of films with pagination, sorting, and total count of genres.
        """
        return await self._fetch_films(page_size, page_number, sort)

    async def search(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[FilmDetail], int]:
        """
        Search for films based on a query string with pagination, sorting, and total count of results.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["title", "description"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_films(page_size, page_number, sort, search_body)

    async def _fetch_films(
            self,
            page_size: int,
            page_number: int,
            sort: str | None = None,
            query: dict | None = None
    ) -> Tuple[List[FilmDetail], int]:
        """
        Helper method to fetch list of films with pagination, sorting, total count, and caching.
        """

        cache_key_parts = [f"films:list:{page_number}:{page_size}:{sort}"]
        if query:
            cache_key_parts.append(str(query))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self.cache_service.get_list_from_cache(cache_key, FilmDetail)
        if cached_data:
            return cached_data

        try:
            films, total_items = await self.request_service.response_list('movies', FilmDetail, page_size, page_number, sort, query)
            await self.cache_service.put_list_to_cache(cache_key, films, total_items)

            return films, total_items
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error: {str(e)}")


@lru_cache()
def get_film_service(
        cache_service: CacheService = Depends(get_cache_service),
        request_service: RequestService = Depends(get_request_service)
) -> FilmService:
    return FilmService(cache_service, request_service)
