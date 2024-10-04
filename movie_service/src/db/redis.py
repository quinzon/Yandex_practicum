from redis.asyncio import Redis

redis_client: Redis | None = None


async def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    return redis_client
