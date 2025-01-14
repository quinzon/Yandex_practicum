import json
import time

from aiokafka import AIOKafkaProducer

from bigdata_service.src.config import settings
from bigdata_service.src.logging_config import logger


def json_serializer(value: dict) -> bytes:
    return json.dumps(value).encode('utf-8')


class KafkaEventProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_broker_urls,
            value_serializer=json_serializer,
            acks=1,
        )
        self.is_started = False

    async def start(self):
        if not self.is_started:
            logger.info('Starting Kafka producer...')
            await self.producer.start()
            self.is_started = True

    async def stop(self):
        if self.is_started:
            logger.info('Stopping Kafka producer...')
            await self.producer.stop()
            self.is_started = False

    async def send_event(self, event_type: str, user_id: str, payload: dict):
        topic = event_type
        key = user_id.encode('utf-8')
        event_data = {
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': int(time.time()),
            'payload': payload,
        }

        logger.info('Sending event | topic=%s, user_id=%s', topic, user_id)
        try:
            await self.producer.send(topic, key=key, value=event_data)
            logger.info('Event successfully sent | topic=%s', topic)
        except Exception as e:
            logger.error('Failed to send event: %s', str(e), exc_info=True)
            raise


kafka_producer = KafkaEventProducer()
