from functools import lru_cache

from notification_service.src.core.rabbitmq import RabbitMQProducer, rabbitmq
from notification_service.src.model.notification import Notification, NotificationResponse


class NotificationService:
    def __init__(self, rabbit_client: RabbitMQProducer):
        self.rabbit_client = rabbit_client

    async def send_notification(self, notification: Notification,
                                request_id: str) -> NotificationResponse:
        routing_key = f'notifications.{notification.type.value}'
        delay_ms = notification.get_delay_ms()

        headers = {'x-request-id': request_id}

        if delay_ms and notification.is_delayed:
            headers['x-delay'] = delay_ms

        await self.rabbit_client.publish(routing_key, notification.model_dump(), headers, delay_ms,
                                         notification.priority)

        return NotificationResponse(
            status='queued',
            type=notification.type,
            is_delayed=notification.is_delayed,
            send_time=notification.send_time,
            priority=notification.priority,
            routing_key=routing_key
        )


@lru_cache()
def get_notification_service() -> NotificationService:
    return NotificationService(rabbitmq)
