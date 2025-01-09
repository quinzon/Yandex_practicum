from functools import lru_cache
from typing import Optional, Dict, Any

from fastapi import Depends

from ugc_service.src.core.exceptions import DuplicateException
from ugc_service.src.models.documents import Bookmark
from ugc_service.src.models.models import PaginatedResponse, BookmarkResponse, BookmarkRequest
from ugc_service.src.repository.bookmark import BookmarkRepository, get_bookmark_repository


class BookmarkService:
    def __init__(self, repository: BookmarkRepository):
        self.repository = repository

    async def create_bookmark(self, bookmark_req: BookmarkRequest,
                              user_id: str) -> BookmarkResponse:
        bookmark_doc = Bookmark(
            user_id=user_id,
            film_id=bookmark_req.film_id
        )
        try:
            bookmark_doc = await self.repository.create(bookmark_doc)
        except Exception as e:
            if 'duplicate key error' in str(e).lower():
                raise DuplicateException('Bookmark already exists') from e
            raise

        return BookmarkResponse(
            id=str(bookmark_doc.id),
            user_id=bookmark_doc.user_id,
            film_id=bookmark_doc.film_id,
            timestamp=bookmark_doc.timestamp
        )

    async def get_bookmark(self, bookmark_id: str) -> Optional[BookmarkResponse]:
        bookmark_doc = await self.repository.get(bookmark_id)
        if not bookmark_doc:
            return None

        return BookmarkResponse(
            id=str(bookmark_doc.id),
            user_id=bookmark_doc.user_id,
            film_id=bookmark_doc.film_id,
            timestamp=bookmark_doc.timestamp
        )

    async def delete_bookmark(self, bookmark_id: str) -> None:
        await self.repository.delete(bookmark_id)

    async def search_bookmarks(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None
    ) -> PaginatedResponse[BookmarkResponse]:
        count, bookmarks = await self.repository.find(filters, skip, limit, sort_by)

        items = [
            BookmarkResponse(
                id=str(bookmark.id),
                user_id=bookmark.user_id,
                film_id=bookmark.film_id,
                timestamp=bookmark.timestamp
            )
            for bookmark in bookmarks
        ]

        return PaginatedResponse(total=count, items=items)


@lru_cache()
def get_bookmark_service(
        repository: BookmarkRepository = Depends(get_bookmark_repository)
) -> BookmarkService:
    return BookmarkService(repository)
