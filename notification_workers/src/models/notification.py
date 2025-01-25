from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class NotificationMessage(BaseModel):
    type: str = Field(...)
    user_id: str | None = Field(None)
    template_id: str = Field(...)
    subject: str | None = Field(None)
    text: str | None = Field(None)
    is_delayed: bool = Field(False)
    send_time: Optional[datetime] = Field(None)
    priority: int = Field(5)
    recipient_group: str | None = Field(None)


class RecipientData(BaseModel):
    user_id: str
    email: str | None = None
    phone: str | None = None
    push_token: str | None = None
    name: str | None = None


class EnrichedNotification(BaseModel):
    type: str
    subject: str | None
    text: str
    recipients: List[RecipientData]
