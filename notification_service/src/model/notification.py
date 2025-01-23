from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'


class Notification(BaseModel):
    type: NotificationType = Field(...)
    user_id: str = Field(...)
    template_id: str = Field(...)
    subject: str = Field(...)
    text: str = Field(...)
    is_delayed: bool = Field(False)
    send_time: str | None = Field(None)
    priority: int = Field(0, ge=0, le=10)
    recipient_group: str = Field(None)

    def get_delay_ms(self) -> int:
        if not self.is_delayed or not self.send_time:
            return 0

        send_time_object = datetime.fromisoformat(self.send_time)
        if send_time_object.tzinfo is None:
            raise ValueError('send_time must include timezone info.')

        send_time_utc = send_time_object.astimezone(timezone.utc)
        now_utc = datetime.now(timezone.utc)

        delay_ms = max(0, int((send_time_utc - now_utc).total_seconds() * 1000))
        return delay_ms


class NotificationResponse(BaseModel):
    status: str = Field(...)
    type: NotificationType = Field(...)
    is_delayed: bool = Field(...)
    send_time: str | None = Field(None)
    priority: int = Field(...)
    routing_key: str = Field(...)
