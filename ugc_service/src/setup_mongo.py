from pymongo import MongoClient
from beanie import init_beanie
import logging

from ugc_service.src.core.config import settings
from ugc_service.src.core.mongo import mongo_client
from ugc_service.src.models.documents import Bookmark, FilmRating, Review

logger = logging.getLogger(__name__)


async def init_mongo_and_shard():
    await init_beanie(database=mongo_client, document_models=[Bookmark, FilmRating, Review])
    logger.info('Beanie initialized with database and document models')

    sync_client = MongoClient(settings.mongo_url)
    admin_db = sync_client['admin']

    try:
        admin_db.command('enableSharding', settings.mongo_db)
        logger.info(f'Sharding enabled for database {settings.mongo_db}')

        for collection_name, shard_key in [
            ('bookmarks', {'user_id': 'hashed'}),
            ('film_ratings', {'film_id': 'hashed'}),
            ('reviews', {'film_id': 'hashed'}),
        ]:
            admin_db.command(
                'shardCollection',
                f'{settings.mongo_db}.{collection_name}',
                key=shard_key
            )
            logger.info('Collection %s sharded successfully', collection_name)

    except Exception as e:
        logger.warning('Shard initialization error: %s', e)
