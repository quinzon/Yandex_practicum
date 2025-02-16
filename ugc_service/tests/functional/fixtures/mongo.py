import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from ugc_service.tests.functional.settings import test_settings


@pytest.fixture(scope='function', autouse=True)
async def cleanup_mongo():
    client = AsyncIOMotorClient(test_settings.mongo_url)

    test_db_name = test_settings.mongo_db

    yield

    await client.drop_database(test_db_name)
    client.close()
