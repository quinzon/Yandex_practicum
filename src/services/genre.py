import json
from functools import lru_cache
from typing import Optional, List
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException, Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    SORTABLE_FIELDS = {
        "name": "name.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.redis = redis

    async def get_genre_by_id(self, genre_id: UUID) -> Optional[Genre]:
        """
        Get a genre by its ID. Cache the result if found.
        """
        cache_key = f"genre:{genre_id}"
        cached_data = await self._get_single_genre_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.get(index='genres', id=str(genre_id))
            genre = Genre(**response['_source'])
            await self._put_single_genre_to_cache(cache_key, genre)
            return genre
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Genre not found: {str(e)}")

    async def get_all_genres(
            self,
            page_size: int = 10,
            page_number: int = 1,
            sort: Optional[str] = None
    ) -> List[Genre]:
        """
        Get a list of genres with pagination and sorting.
        """
        return await self._fetch_genres(page_size=page_size, page_number=page_number, sort=sort)

    async def search_genres(
            self,
            query: str,
            page_size: int = 10,
            page_number: int = 1,
            sort: Optional[str] = None
    ) -> List[Genre]:
        """
        Search for genres based on a query string with pagination and sorting.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_genres(page_size=page_size, page_number=page_number, sort=sort, search_body=search_body)

    async def _fetch_genres(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str] = None,
            search_body: Optional[dict] = None
    ) -> List[Genre]:
        """
        Helper method to fetch genres from Elasticsearch with pagination, sorting, and optional search.
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

        cache_key_parts = [f"genres:list:{page_number}:{page_size}:{sort}"]
        if search_body:
            cache_key_parts.append(str(search_body))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.search(index='genres', body=body)
            genres = [Genre(**doc['_source']) for doc in response['hits']['hits']]

            await self._put_to_cache(cache_key, genres)

            return genres
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Elasticsearch error: {str(e)}")

    async def _get_from_cache(self, cache_key: str) -> Optional[List[Genre]]:
        """
        Retrieve data from Redis cache.
        """
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return [Genre.parse_raw(item) for item in json.loads(cached_data)]
        return None

    async def _put_to_cache(self, cache_key: str, data: List[Genre]) -> None:
        """
        Store data in Redis cache.
        """
        serialized_data = json.dumps([genre.json() for genre in data])
        await self.redis.set(cache_key, serialized_data, ex=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _get_single_genre_from_cache(self, cache_key: str) -> Optional[Genre]:
        """
        Retrieve a single genre from Redis cache.
        """
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return Genre.parse_raw(cached_data)
        return None

    async def _put_single_genre_to_cache(self, cache_key: str, genre: Genre) -> None:
        """
        Store a single genre in Redis cache.
        """
        await self.redis.set(cache_key, genre.json(), ex=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(redis, elastic)
