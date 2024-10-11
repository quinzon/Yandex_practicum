from typing import Optional, List

from uuid import UUID

from pydantic import BaseModel

from auth_service.src.models.dto.common import BaseDto


class RefreshToken(BaseDto):
    user_id: UUID
    token_value: str


class TokenResponse(BaseDto):
    access_token: str
    refresh_token: Optional[str] = None


class TokenData(BaseDto):
    user_id: str
    email: str
    roles: List[str]


class RefreshTokenRequest(BaseModel):
    token_value: str
