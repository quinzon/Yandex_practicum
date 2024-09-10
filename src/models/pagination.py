from functools import wraps
from typing import List, Generic, TypeVar, Callable, Type

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page_size: int
    page_number: int
    total_items: int
    total_pages: int


class Pagination(Generic[T], BaseModel):
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
