import json
from functools import lru_cache
from typing import Tuple, List, Type, Union

from redis.asyncio import Redis
from fastapi import Depends

from movie_service.src.db.redis import get_redis
from movie_service.src.models.film import Film, FilmDetail
from movie_service.src.models.genre import Genre
from movie_service.src.models.person import Person, PersonFilmsParticipant


class CacheService:
    CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_list_from_cache(
            self,
            cache_key: str,
            model: Type[Union[Film, Genre, Person]]
    ) -> Tuple[List[Union[Film, FilmDetail, Genre, Person, PersonFilmsParticipant]], int] | None:
        """
        Retrieve list of data and total_items from Redis cache.
        """
        cached_data = await self.redis.get(cache_key)
        if not cached_data:
            return None

        cached_dict = json.loads(cached_data)
        data = [model.parse_raw(item) for item in cached_dict['items']]
        total_items = cached_dict['total_items']
        return data, total_items

    async def put_list_to_cache(
            self,
            cache_key: str,
            films: List[Union[Film, FilmDetail, Genre, Person, PersonFilmsParticipant]],
            total_items: int
    ) -> None:
        """
        Store list of data and total_items in Redis cache.
        """
        serialized_data = json.dumps({
            "items": [film.json() for film in films],
            "total_items": total_items
        })
        await self.redis.set(cache_key, serialized_data, ex=self.CACHE_EXPIRE_IN_SECONDS)

    async def get_from_cache_by_id(
            self,
            cache_key: str,
            model: Type[Union[Film, FilmDetail, Genre, Person]]
    ) -> Union[Film, FilmDetail, Genre, Person, PersonFilmsParticipant] | None:
        """
        Retrieve data by id from Redis cache.
        """
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return model.parse_raw(data)

    async def put_to_cache_by_id(
            self,
            cache_key: str,
            data: Film | FilmDetail | Genre | Person | PersonFilmsParticipant
    ) -> None:
        """
        Store data by id in Redis cache.
        """
        await self.redis.set(cache_key, data.json(), self.CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_cache_service(
        redis: Redis = Depends(get_redis)
) -> CacheService:
    return CacheService(redis)
