from motor.motor_asyncio import AsyncIOMotorClient

from ugc_service.src.core.config import settings

mongo_client = AsyncIOMotorClient(settings.mongo_url)[settings.mongo_db]
