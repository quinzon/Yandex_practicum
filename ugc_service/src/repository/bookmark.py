from functools import lru_cache
from typing import Type

from ugc_service.src.models.documents import Bookmark
from ugc_service.src.repository.base import BaseRepository


class BookmarkRepository(BaseRepository[Bookmark]):
    def get_model(self) -> Type[Bookmark]:
        return Bookmark


@lru_cache()
def get_bookmark_repository() -> BookmarkRepository:
    return BookmarkRepository()
