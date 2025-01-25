import logging
import httpx
import json

from notification_workers.src.services.senders.base import BaseSender
from notification_workers.src.models.notification import EnrichedNotification

logger = logging.getLogger(__name__)


class PushSender(BaseSender):
    def __init__(self, push_service_url: str):
        self.push_service_url = push_service_url

    async def send(self, notification: EnrichedNotification) -> None:
        recipients = [r for r in notification.recipients if r.user_id]
        if not recipients:
            logger.warning('No valid user_id in recipients. Skip push sending.')
            return

        async with httpx.AsyncClient() as client:
            for r in recipients:
                payload = {
                    'user_id': r.user_id,
                    'message': notification.text
                }
                url = f'{self.push_service_url}/api/v1/message/send'
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    logger.info(
                        'Sent push message to user_id=%s, status_code=%d',
                        r.user_id, response.status_code
                    )
                except httpx.HTTPError as exc:
                    logger.exception(
                        'Failed to send push message to user_id=%s',
                        r.user_id
                    )
