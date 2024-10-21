from typing import List
from uuid import UUID

from pydantic import BaseModel

from auth_service.src.models.dto.common import BaseDto
from auth_service.src.models.dto.role import RoleResponse


class RefreshToken(BaseDto):
    user_id: UUID
    token_value: str


class TokenResponse(BaseDto):
    access_token: str
    refresh_token: str | None = None


class TokenData(BaseDto):
    user_id: str
    email: str
    roles: List[str] | None


class AccessTokenRequest(BaseModel):
    access_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
