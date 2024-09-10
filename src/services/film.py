from functools import lru_cache
from typing import Optional, List, Tuple
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    SORTABLE_FIELDS = {
        "imdb_rating": "imdb_rating",
        "title": "title.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

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

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
