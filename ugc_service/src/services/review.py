from functools import lru_cache
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import Depends

from ugc_service.src.models.documents import Review
from ugc_service.src.repository.review import get_review_repository, ReviewRepository


class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def create_review(self, review: Review) -> Review:
        return await self.repository.create(review)

    async def get_review(self, review_id: UUID) -> Optional[Review]:
        return await self.repository.get(review_id)

    async def update_review(self, review_id: UUID, review: Review) -> Optional[Review]:
        return await self.repository.update(review_id, review)

    async def delete_review(self, review_id: UUID) -> None:
        await self.repository.delete(review_id)

    async def search_reviews(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None,
    ) -> List[Review]:
        return await self.repository.find(filters, skip, limit, sort_by)


@lru_cache()
def get_review_service(
        repository: ReviewRepository = Depends(get_review_repository)
) -> ReviewService:
    return ReviewService(repository)
