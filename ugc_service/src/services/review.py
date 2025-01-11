from functools import lru_cache
from typing import Optional, Dict, Any

from fastapi import Depends

from ugc_service.src.core.exceptions import DuplicateException
from ugc_service.src.models.documents import Review
from ugc_service.src.models.models import PaginatedResponse, ReviewResponse, ReactionType, \
    ReviewCreate, ReviewUpdate
from ugc_service.src.repository.review import get_review_repository, ReviewRepository


class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    async def create_review(self, data: ReviewCreate) -> ReviewResponse:
        review_doc = Review(
            user_id=data.user_id,
            film_id=data.film_id,
            review_text=data.review_text,
            rating=data.rating,
        )
        try:
            review_doc = await self.repository.create(review_doc)
        except Exception as e:
            if 'duplicate key error' in str(e).lower():
                raise DuplicateException(
                    'Review with this user_id and film_id already exists') from e
            raise

        return self._to_response(review_doc)

    async def get_review(self, review_id: str) -> Optional[ReviewResponse]:
        doc = await self.repository.get(review_id)
        if not doc:
            return None
        return self._to_response(doc)

    async def update_review(self, review_id: str, data: ReviewUpdate) -> Optional[ReviewResponse]:
        doc = await self.repository.get(review_id)
        if not doc:
            return None

        doc.review_text = data.review_text
        doc.rating = data.rating

        updated = await self.repository.update(review_id, doc)
        if not updated:
            return None
        return self._to_response(updated)

    async def delete_review(self, review_id: str) -> None:
        await self.repository.delete(review_id)

    async def search_reviews(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None,
    ) -> PaginatedResponse[ReviewResponse]:
        count, docs = await self.repository.find(filters, skip, limit, sort_by)
        items = [self._to_response(doc) for doc in docs]
        return PaginatedResponse(total=count, items=items)

    async def toggle_reaction(self, review_id: str, user_id: str, reaction: ReactionType) -> bool:
        doc = await self.repository.get(review_id)
        if not doc:
            return False

        if reaction == ReactionType.like:
            if user_id in doc.likes:
                doc.likes.remove(user_id)
            else:
                doc.likes.add(user_id)
                doc.dislikes.discard(user_id)
        elif reaction == ReactionType.dislike:
            if user_id in doc.dislikes:
                doc.dislikes.remove(user_id)
            else:
                doc.dislikes.add(user_id)
                doc.likes.discard(user_id)

        await self.repository.update(review_id, doc)
        return True

    def _to_response(self, doc: Review) -> ReviewResponse:
        return ReviewResponse(
            id=str(doc.id),
            user_id=doc.user_id,
            film_id=doc.film_id,
            review_text=doc.review_text,
            rating=doc.rating,
            likes_count=len(doc.likes),
            dislikes_count=len(doc.dislikes),
            timestamp=doc.timestamp,
        )


@lru_cache()
def get_review_service(
        repository: ReviewRepository = Depends(get_review_repository)
) -> ReviewService:
    return ReviewService(repository)
