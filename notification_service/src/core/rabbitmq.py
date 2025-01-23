import json

from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import DeliveryMode

from notification_service.src.core.config import settings
from notification_service.src.core.logger import logger


class RabbitMQProducer:
    def __init__(self):
        self.rabbitmq_url = settings.rabbitmq_url
        self.exchange_name = settings.exchange_name
        self.delayed_exchange_name = settings.delayed_exchange_name
        self.exchange = None
        self.delayed_exchange = None
        self.__connection = None
        self.__channel = None

    async def connect(self):
        self.__connection = await connect_robust(self.rabbitmq_url)
        self.__channel = await self.__connection.channel()

        self.exchange = await self.__channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True
        )

        self.delayed_exchange = await self.__channel.declare_exchange(
            self.delayed_exchange_name,
            ExchangeType.X_DELAYED_MESSAGE,
            durable=True,
            arguments={'x-delayed-type': 'topic'}
        )

    async def initialize_queues(self):
        queues = settings.get_queue_list()

        for queue_name in queues:
            queue = await self.__channel.declare_queue(
                f'{settings.prefix}_{queue_name}',
                durable=True,
                arguments={'x-max-priority': settings.max_priority}
            )

            routing_key = f'{settings.prefix}.{queue_name}'

            logger.debug('Initializing queue %s with routing key %s', queue_name, routing_key)

            await queue.bind(self.exchange_name, routing_key=routing_key)
            await queue.bind(self.delayed_exchange_name,
                             routing_key=routing_key)

    async def publish(self, routing_key: str, message: dict, headers: dict, delay_ms: int = 0,
                      priority: int = 0):

        exchange = self.delayed_exchange if delay_ms > 0 else self.exchange

        logger.debug('Message publishing: %s, delay is %s', message, delay_ms)
        logger.debug('Message exchange: %s', exchange.name)

        await exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                headers=headers,
                priority=priority,
            ),
            routing_key=routing_key,
        )

    async def close(self):
        if self.__connection:
            await self.__connection.close()


rabbitmq = RabbitMQProducer()
