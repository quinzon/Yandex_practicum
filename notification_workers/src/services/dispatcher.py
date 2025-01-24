import logging
from typing import Dict

from notification_workers.src.models.notification import EnrichedNotification
from notification_workers.src.services.senders.base import BaseSender

logger = logging.getLogger(__name__)


class DispatcherService:
    def __init__(self, senders_map: Dict[str, BaseSender]):
        self.senders_map = senders_map

    async def dispatch(self, enriched: EnrichedNotification) -> None:
        sender = self.senders_map.get(enriched.type)
        if not sender:
            logger.error('Unknown notification type: %s', enriched.type)
            raise ValueError(f'Unknown notification type: {enriched.type}')
        await sender.send(enriched)
