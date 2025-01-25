from abc import ABC, abstractmethod

from notification_workers.src.models.notification import EnrichedNotification


class BaseSender(ABC):
    @abstractmethod
    async def send(self, notification: EnrichedNotification) -> None:
        ...
