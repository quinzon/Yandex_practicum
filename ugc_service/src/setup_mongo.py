from pymongo import MongoClient
from beanie import init_beanie

from ugc_service.src.core.mongo import mongo_client
from ugc_service.src.models.documents import Bookmark, FilmRating, Review
from ugc_service.src.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def init_mongo_and_shard():
    db = mongo_client.get_default_database()

    await init_beanie(database=db, document_models=[Bookmark, FilmRating, Review])
    logger.info('Beanie initialized with database and document models')

    sync_client = MongoClient(settings.mongo_url)

    try:
        for collection_name, shard_key in [
            ('bookmarks', {'user_id': 'hashed'}),
            ('filmratings', {'film_id': 'hashed'}),
            ('reviews', {'film_id': 'hashed'}),
        ]:
            sync_client.admin.command(
                'shardCollection',
                f'{db.name}.{collection_name}',
                key=shard_key
            )
            logger.info('Collection % sharded successfully', collection_name)
    except Exception as e:
        logger.warning('Shard initialization error: %', e)
