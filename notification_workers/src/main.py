import asyncio
import json

from aio_pika import IncomingMessage, ExchangeType
from notification_workers.src.core.config import settings
from notification_workers.src.core.logger import logger
from notification_workers.src.core.rabbitmq import get_rabbitmq_connection
from notification_workers.src.models.notification import NotificationMessage
from notification_workers.src.services.dispatcher import DispatcherService
from notification_workers.src.services.enrich import EnrichService
from notification_workers.src.services.senders.email import EmailSender
from notification_workers.src.services.senders.push import PushSender
from notification_workers.src.services.senders.sms import SmsSender


enrich_service: EnrichService | None = None
dispatcher: DispatcherService | None = None


async def on_message(message: IncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        try:
            body_str = message.body.decode('utf-8')
            data = json.loads(body_str)

            logger.info(
                'Received message from queue=%s: %s',
                message.routing_key,
                data
            )

            notification_msg = NotificationMessage(**data)

            if enrich_service is None or dispatcher is None:
                logger.error('Services are not initialized.')
                return

            enriched = await enrich_service.get_enriched_notification(notification_msg)
            await dispatcher.dispatch(enriched)

            logger.info('Successfully processed message: %s', data)

        except Exception:
            logger.exception('Error processing message. NACK -> DLX (if configured).')
            raise


async def setup_services() -> None:
    global enrich_service, dispatcher

    enrich_service = EnrichService(settings.admin_service_url)

    email_sender = EmailSender(
        sendgrid_email_key=settings.sendgrid_email_key,
        default_from_email=settings.email_from
    )
    sms_sender = SmsSender()
    push_sender = PushSender(settings.push_service_url)

    dispatcher = DispatcherService({
        'email': email_sender,
        'sms': sms_sender,
        'push': push_sender
    })


async def main() -> None:
    await setup_services()

    connection = await get_rabbitmq_connection()
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    dlx_name = 'notifications_dlx'
    dlx_exchange = await channel.declare_exchange(
        dlx_name,
        ExchangeType.DIRECT,
        durable=True
    )

    dlq_name = 'notifications_dlq'
    dlq_queue = await channel.declare_queue(dlq_name, durable=True)

    await dlq_queue.bind(dlx_exchange, routing_key=dlx_name)

    queue_names = [
        'notifications_email',
        'notifications_sms',
        'notifications_push'
    ]

    for q_name in queue_names:
        queue = await channel.declare_queue(
            q_name,
            durable=True,
            arguments={
                'x-max-priority': 10,
                'x-dead-letter-exchange': dlx_name,
                'x-dead-letter-routing-key': dlx_name
            }
        )
        await channel.set_qos(prefetch_count=10)
        await queue.consume(on_message)
        logger.info('Subscribed to queue: %s', q_name)

    logger.info('Worker started, consuming multiple queues...')
    await asyncio.Future()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down...')
