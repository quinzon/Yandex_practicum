import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from ugc_service.tests.functional.settings import test_settings
from ugc_service.tests.functional.utils.backoff import backoff

logger = logging.getLogger(__name__)


@backoff()
async def wait_for_mongo():
    mongo_client = AsyncIOMotorClient(test_settings.mongo_url)
    try:
        result = await mongo_client.admin.command('ping')
        if result.get('ok') == 1:
            logger.debug('MongoDB is available!')
            return True
        else:
            raise Exception('MongoDB ping failed')
    except Exception as e:
        logger.error('Waiting for MongoDB... Exception: %s', e)
        raise Exception('Waiting for MongoDB...') from e


if __name__ == '__main__':
    asyncio.run(wait_for_mongo())
