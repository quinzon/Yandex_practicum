from push_service.src.storage import redis_storage


async def push_sender(user_id, message):
    await redis_storage.put_to_storage_by_id(user_id, message)
