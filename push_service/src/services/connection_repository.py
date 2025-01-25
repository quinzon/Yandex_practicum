from functools import lru_cache

from redis.asyncio import Redis
from fastapi import Depends

from push_service.src.db.redis import get_redis


class ConnectionRepositoryService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_list_by_id(self, user_id: str) -> list | None:
        data = await self.redis.lrange(user_id, 0, -1)
        if not data:
            return None
        return data

    async def put_by_id(self, user_id: str, token: str) -> None:
        await self.redis.rpush(user_id, token)

    async def remove_value_by_id(self, user_id: str, token: str) -> None:
        await self.redis.lrem(user_id, 0, token)
        length = await self.redis.llen(user_id)

        if length == 0:
            await self.redis.delete(user_id)


@lru_cache()
def get_connection_repository(
        redis: Redis = Depends(get_redis)
) -> ConnectionRepositoryService:
    return ConnectionRepositoryService(redis)
