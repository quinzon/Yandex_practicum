import asyncio

from redis.asyncio import Redis

from auth_service.tests.functional.settings import test_settings
from auth_service.tests.functional.utils.backoff import backoff
from auth_service.tests.functional.utils.logger import logger


@backoff(start_sleep_time=0.5, factor=2, border_sleep_time=10)
async def wait_for_redis():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port, db=0)
    if await redis_client.ping():
        logger.debug('Redis is available!')
        return True
    raise Exception('Waiting for Redis...')

if __name__ == '__main__':
    asyncio.run(wait_for_redis())
