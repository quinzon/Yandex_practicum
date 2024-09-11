from functools import lru_cache
from typing import Optional, List, Tuple
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import FilmDetail
from src.services.cache import CacheService


class FilmService(CacheService):
    SORTABLE_FIELDS = {
        "imdb_rating": "imdb_rating",
        "title": "title.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis)
        self.elastic = elastic

    async def get_film_by_id(self, film_id: str) -> Optional[FilmDetail]:
        """
        Retrieve a film by its unique ID.
        """
        cache_key = f"film:{film_id}"
        cached_data = await self._get_from_cache_by_id(cache_key, FilmDetail)
        if cached_data:
            return cached_data
        try:
            response = await self.elastic.get(index='movies', id=film_id)
            film = FilmDetail(**response['_source'])
            await self._put_to_cache_by_id(cache_key, film)
            return film
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

    async def get_films_by_person_id(self, person_id: UUID, from_: int = 0, size: int = 50,
                                     sort: Optional[str] = "-imdb_rating") -> Tuple[List[dict], int]:
        """
        Fetch all films where a person (by person_id) appears in any role: actor, writer, or director.
        Support pagination and sorting.
        """
        sort_order = "asc"
        if sort.startswith("-"):
            sort_order = "desc"
            sort = sort[1:]

        sort_field = self.SORTABLE_FIELDS.get(sort, "imdb_rating")

        body = {
            "from": from_,
            "size": size,
            "query": {
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
            },
            "sort": [{sort_field: {"order": sort_order}}]
        }

        try:
            response = await self.elastic.search(index='movies', body=body)
            total_items = response['hits']['total']['value']
            return response['hits']['hits'], total_items
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching films for person: {str(e)}")

    async def get_films_by_genre_id(self, genre_id: UUID, from_: int = 0, size: int = 50,
                                    sort: Optional[str] = "-imdb_rating") -> Tuple[List[dict], int]:
        """
        Fetch all films where the genre matches genre_id.
        Support pagination and sorting.
        """
        sort_order = "asc"
        if sort.startswith("-"):
            sort_order = "desc"
            sort = sort[1:]

        sort_field = self.SORTABLE_FIELDS.get(sort, "imdb_rating")

        body = {
            "from": from_,
            "size": size,
            "query": {
                "nested": {
                    "path": "genres",
                    "query": {
                        "term": {"genres.id": str(genre_id)}
                    }
                }
            },
            "sort": [{sort_field: {"order": sort_order}}]
        }

        try:
            response = await self.elastic.search(index='movies', body=body)
            total_items = response['hits']['total']['value']
            return response['hits']['hits'], total_items
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching films for genre: {str(e)}")

    async def get_all_films(
            self,
            page_size: int = 50,
            page_number: int = 1,
            sort: Optional[str] = None
    ) -> Tuple[List[FilmDetail], int]:
        """
        Get a list of films with pagination, sorting, and total count of genres.
        """
        return await self._fetch_films(page_size=page_size, page_number=page_number, sort=sort)

    async def search_films(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            sort: Optional[str] = None
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
        return await self._fetch_films(page_size=page_size, page_number=page_number, sort=sort,
                                       search_body=search_body)

    async def _fetch_films(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str] = None,
            search_body: Optional[dict] = None
    ) -> Tuple[List[FilmDetail], int]:
        """
        Helper method to fetch films from Elasticsearch with pagination, sorting, total count, and caching.
        """
        from_ = (page_number - 1) * page_size

        sort_order = "asc"
        if sort and sort.startswith('-'):
            sort_order = "desc"
            sort = sort[1:]

        sort_field = self.SORTABLE_FIELDS.get(sort, sort)

        body = {
            "from": from_,
            "size": page_size,
            "query": search_body if search_body else {"match_all": {}},
            "sort": [{sort_field: {"order": sort_order}}] if sort_field else []
        }

        cache_key_parts = [f"films:list:{page_number}:{page_size}:{sort}"]
        if search_body:
            cache_key_parts.append(str(search_body))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self._get_list_from_cache(cache_key, FilmDetail)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.search(index='movies', body=body)
            films = [FilmDetail(**doc['_source']) for doc in response['hits']['hits']]
            total_items = response['hits']['total']['value']

            await self._put_list_to_cache(cache_key, films, total_items)

            return films, total_items
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Elasticsearch error: {str(e)}")


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
