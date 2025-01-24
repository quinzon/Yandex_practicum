from redis.asyncio import Redis
from push_service.src.config import settings


class DictionaryStorage:
    TIME_EXPIRE_IN_SECONDS = 60 * 60 * 5

    def __init__(self):
        self.redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )

    async def get_list_from_storage_by_id(self, user_id: str) -> list | None:
        data = await self.redis.lrange(user_id, 0, -1)
        if not data:
            return None
        return data

    async def put_to_storage_by_id(self, user_id: str, token: str) -> None:
        await self.redis.rpush(user_id, token)
        await self.redis.expire(user_id, self.TIME_EXPIRE_IN_SECONDS)

    async def remove_value_from_storage_by_id(self, user_id: str, token: str) -> None:
        await self.redis.lrem(user_id, 0, token)
        length = await self.redis.llen(user_id)

        if length == 0:
            await self.redis.delete(user_id)


redis_storage = DictionaryStorage()
