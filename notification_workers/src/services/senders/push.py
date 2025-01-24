import logging

from notification_workers.src.models.notification import EnrichedNotification
from notification_workers.src.services.senders.base import BaseSender

logger = logging.getLogger(__name__)


class PushSender(BaseSender):
    async def send(self, notification: EnrichedNotification) -> None:
        push_tokens = [r.push_token for r in notification.recipients if r.push_token]
        if not push_tokens:
            logger.warning('No push tokens found: skip sending push notifications.')
            return

        logger.info('Sending push notification to %s. Text: %s', push_tokens, notification.text)
