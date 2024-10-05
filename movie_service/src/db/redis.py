from redis.asyncio import Redis

redis_client: Redis | None = None


async def get_redis() -> Redis:
    return redis_client
