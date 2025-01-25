import aio_pika

from notification_workers.src.core.config import settings
from notification_workers.src.core.logger import logger


async def get_rabbitmq_connection() -> aio_pika.RobustConnection:
    logger.info('Connecting to RabbitMQ...')
    return await aio_pika.connect_robust(settings.rabbitmq_url)
