from functools import lru_cache
from typing import Type

from ugc_service.src.models.documents import Review
from ugc_service.src.repository.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def get_model(self) -> Type[Review]:
        return Review


@lru_cache()
def get_review_repository() -> ReviewRepository:
    return ReviewRepository()
