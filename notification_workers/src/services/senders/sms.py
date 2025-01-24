from notification_workers.src.models.notification import EnrichedNotification
from notification_workers.src.services.senders.base import BaseSender


class SmsSender(BaseSender):

    async def send(self, notification: EnrichedNotification) -> None:
        raise NotImplementedError()
