from pydantic import BaseModel
from uuid import UUID


class SubscriptionResponse(BaseModel):
    id: UUID
    name: str
    price: float
    duration_days: int

    class Config:
        orm_mode = True
