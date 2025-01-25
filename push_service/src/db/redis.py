from redis.asyncio import Redis

from push_service.src.core.config import get_redis_settings

redis_client: Redis | None = None


def get_redis() -> Redis:
    settings = get_redis_settings()
    return Redis.from_url(settings.redis_url(), decode_responses=True)
