from typing import Optional

from pydantic import BaseModel
from uuid import UUID


class RefreshToken(BaseModel):
    user_id: UUID
    token_value: str

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
