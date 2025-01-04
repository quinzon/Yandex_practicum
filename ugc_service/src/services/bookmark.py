from functools import lru_cache
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import Depends

from ugc_service.src.models.documents import Bookmark
from ugc_service.src.repository.bookmark import BookmarkRepository, get_bookmark_repository


class BookmarkService:
    def __init__(self, repository: BookmarkRepository):
        self.repository = repository

    async def create_bookmark(self, bookmark: Bookmark) -> Bookmark:
        return await self.repository.create(bookmark)

    async def get_bookmark(self, bookmark_id: UUID) -> Optional[Bookmark]:
        return await self.repository.get(bookmark_id)

    async def delete_bookmark(self, bookmark_id: UUID) -> None:
        await self.repository.delete(bookmark_id)

    async def search_bookmarks(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None
    ) -> List[Bookmark]:
        return await self.repository.find(filters, skip, limit, sort_by)


@lru_cache()
def get_bookmark_service(
        repository: BookmarkRepository = Depends(get_bookmark_repository)
) -> BookmarkService:
    return BookmarkService(repository)
