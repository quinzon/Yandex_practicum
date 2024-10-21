from functools import wraps
from typing import TypeVar, Callable, List, Generic

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


T = TypeVar("T")


class BaseDto(BaseModel):
    model_config = SettingsConfigDict(
        from_attributes=True,
    )


class ErrorMessages:
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


class Messages:
    SUCCESSFUL_LOGOUT = 'Successful logout'


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
