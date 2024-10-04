import http
from functools import lru_cache
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException, Depends

from movie_service.src.models.film import Film
from movie_service.src.models.genre import Genre
from movie_service.src.services.base import SearchableApiServiceInterface
from movie_service.src.services.cache import CacheService, get_cache_service
from movie_service.src.services.film import FilmService, get_film_service
from movie_service.src.services.request import RequestService, get_request_service


class GenreService(SearchableApiServiceInterface):

    def __init__(self, cache_service: CacheService, request_service: RequestService, film_service: FilmService):
        self.cache_service = cache_service
        self.request_service = request_service
        self.film_service = film_service

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """
        Get a genre by its ID. Cache the result if found.
        """
        cache_key = f"genre:{genre_id}"
        cached_data = await self.cache_service.get_from_cache_by_id(cache_key, Genre)
        if cached_data:
            return cached_data

        try:
            genre = await self.request_service.response_by_id('genres', genre_id, Genre)
            await self.cache_service.put_to_cache_by_id(cache_key, genre)
            return genre
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error occurred: {str(e)}")

    async def get_all(
            self,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Genre], int]:
        """
        Get a list of genres with pagination, sorting, and total count of genres.
        """
        return await self._fetch_genres(page_size, page_number, sort)

    async def search(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Genre], int]:
        """
        Search for genres based on a query string with pagination, sorting, and total count of results.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_genres(page_size, page_number, sort, search_body)

    async def get_genre_films(
            self,
            genre_id: UUID,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> tuple[List[Film], int]:
        """
        Get all films associated with a genre by genre ID, with pagination and sorting.
        """
        return await self.film_service.get_films_by_genre_id(genre_id, page_size, page_number, sort)

    async def _fetch_genres(
            self,
            page_size: int,
            page_number: int,
            sort: str | None = None,
            query: dict | None = None
    ) -> Tuple[List[Genre], int]:
        """
        Helper method to fetch list of films with pagination, sorting, total count, and caching.
        """

        cache_key_parts = [f"genres:list:{page_number}:{page_size}:{sort}"]
        if query:
            cache_key_parts.append(str(query))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self.cache_service.get_list_from_cache(cache_key, Genre)
        if cached_data:
            return cached_data

        try:
            genres, total_items = await self.request_service.response_list('genres', Genre, page_size, page_number, sort, query)
            await self.cache_service.put_list_to_cache(cache_key, genres, total_items)

            return genres, total_items
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Error: {str(e)}")


@lru_cache()
def get_genre_service(
        cache_service: CacheService = Depends(get_cache_service),
        request_service: RequestService = Depends(get_request_service),
        film_service: FilmService = Depends(get_film_service)
) -> GenreService:
    return GenreService(cache_service, request_service, film_service)
