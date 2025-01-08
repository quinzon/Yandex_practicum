from functools import lru_cache
from typing import Optional, Dict, Any

from fastapi import Depends

from ugc_service.src.models.documents import Review
from ugc_service.src.models.models import PaginatedResponse, ReviewResponse
from ugc_service.src.repository.review import get_review_repository, ReviewRepository


class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def create_review(self, review: Review) -> Review:
        return await self.repository.create(review)

    async def get_review(self, review_id: str) -> Optional[Review]:
        return await self.repository.get(review_id)

    async def update_review(self, review_id: str, review: Review) -> Optional[Review]:
        return await self.repository.update(review_id, review)

    async def delete_review(self, review_id: str) -> None:
        await self.repository.delete(review_id)

    async def search_reviews(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None,
    ) -> PaginatedResponse[ReviewResponse]:
        count, reviews = await self.repository.find(filters, skip, limit, sort_by)

        items = [
            ReviewResponse(
                id=str(review.id),
                user_id=review.user_id,
                film_id=review.film_id,
                review_text=review.review_text,
                rating=review.rating,
                likes_count=len(review.likes),
                dislikes_count=len(review.dislikes),
                timestamp=review.timestamp
            )
            for review in reviews
        ]

        return PaginatedResponse(total=count, items=items)


@lru_cache()
def get_review_service(
        repository: ReviewRepository = Depends(get_review_repository)
) -> ReviewService:
    return ReviewService(repository)
