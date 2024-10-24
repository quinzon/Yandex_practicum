from functools import wraps
from typing import TypeVar, Callable, List, Generic
from uuid import UUID

from pydantic import BaseModel, model_validator
from pydantic_settings import SettingsConfigDict


T = TypeVar('T')


class BaseDto(BaseModel):
    model_config = SettingsConfigDict(
        from_attributes=True,
    )

    @model_validator(mode='before')
    def convert_uuid_fields(cls, data):
        if isinstance(data, dict):
            for field_name, value in data.items():
                if 'id' in field_name:
                    if isinstance(value, UUID):
                        data[field_name] = str(value)
            return data

        new_data = {}
        for field_name in cls.model_fields:
            value = getattr(data, field_name, None)
            if value is not None:
                if 'id' in field_name and isinstance(value, UUID):
                    new_data[field_name] = str(value)
                else:
                    new_data[field_name] = value
        return new_data


class BaseResponse(BaseModel):
    message: str


class ErrorMessages:
    MISSING_PROVIDER_ID = 'Missing OAuth provider id'
    CREATION_FAILED = 'Creation failed'
    UNSUPPORTED_PROVIDER = 'Unsupported provider'
    PERMISSION_DENIED = 'Permission denied'
    NOT_FOUND = 'Not found'
    INVALID_CREDENTIALS = 'Invalid credentials'
    INVALID_TOKEN = 'Invalid token'
    INVALID_REFRESH_TOKEN = 'Invalid refresh token'
    INVALID_ACCESS_TOKEN = 'Invalid access token'
    TOKEN_EXPIRED = 'Token expired'
    TOKEN_REVOKED = 'Token has been revoked'
    TOKEN_IS_MISSING = 'Authorization header missing or malformed'
    USER_ALREADY_EXISTS = 'User already exists'
    USER_NOT_FOUND = 'User not found'
    NO_EMAIL_PROVIDED = 'No email provided'


class Messages:
    SUCCESSFUL_LOGOUT = 'Successful logout'
    CREATED = 'Created'
    DELETED = 'Deleted'
    PERMISSION_GRANTED = 'Permission granted'


class PaginationMeta(BaseModel):
    page_size: int
    page_number: int
    total_items: int
    total_pages: int


class Pagination(BaseModel, Generic[T]):
    meta: PaginationMeta
    items: List[T]


def create_paginated_response(items: List[T], total_items: int, page_size: int, page_number: int):
    total_pages = (total_items + page_size - 1) // page_size
    meta = PaginationMeta(
        page_size=page_size,
        page_number=page_number,
        total_items=total_items,
        total_pages=total_pages
    )
    return Pagination(meta=meta, items=items)


def paginated_response():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result, total_items = await func(*args, **kwargs)
            page_size = kwargs.get('page_size')
            page_number = kwargs.get('page_number')

            return create_paginated_response(result, total_items, page_size, page_number)
        return wrapper
    return decorator
