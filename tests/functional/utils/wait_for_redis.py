import asyncio
from redis.asyncio import Redis

from tests.functional.settings import test_settings


async def wait_for_redis():
    redis_client = Redis(host=test_settings.redis_host, port=test_settings.redis_port, db=0)
    while True:
        try:
            if await redis_client.ping():
                print("Redis is available!")
                break
        except Exception as e:
            print(f"Waiting for Redis... {e}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(wait_for_redis())
