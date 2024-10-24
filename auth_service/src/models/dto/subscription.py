from uuid import UUID

from auth_service.src.models.dto.common import BaseDto


class SubscriptionResponse(BaseDto):
    id: UUID
    name: str
    price: float
    duration_days: int
