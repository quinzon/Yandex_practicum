from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class BaseDto(BaseModel):
    model_config = SettingsConfigDict(
        from_attributes=True,
    )


class ErrorMessages:
    INVALID_CREDENTIALS = 'Invalid credentials'
    INVALID_TOKEN = 'Invalid token'
    INVALID_REFRESH_TOKEN = 'Invalid refresh token'
    INVALID_ACCESS_TOKEN = 'Invalid access token'
    TOKEN_EXPIRED = 'Token expired'
    TOKEN_REVOKED = 'Token has been revoked'
    TOKEN_IS_MISSING = "Authorization header missing or malformed"
    USER_ALREADY_EXISTS = "User already exists"
    ROLE_ALREADY_EXISTS = "Role already exists"


class Messages:
    SUCCESSFUL_LOGOUT = 'Successful logout'
