import pytest_asyncio
from redis.asyncio import Redis

from auth_service.tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    redis = Redis(host=test_settings.redis_host, port=test_settings.redis_port,
                  db=test_settings.redis_db)
    yield redis
    await redis.close()


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clear_redis_cache(redis_client):
    await redis_client.flushdb()
