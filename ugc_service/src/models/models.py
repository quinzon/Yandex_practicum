from typing import List, TypeVar, Generic, Optional, Dict, Any

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: List[T]


class FilmRatingResponse(BaseModel):
    user_id: UUID
    film_id: UUID
    rating: int = Field(..., ge=0, le=10)
    timestamp: datetime


class FilmAggregatedRatingResponse(BaseModel):
    film_id: UUID
    avg_rating: float
    likes_count: int
    dislikes_count: int
    total_ratings: int


class ReviewResponse(BaseModel):
    id: str
    user_id: UUID
    film_id: UUID
    review_text: str
    rating: int = Field(..., ge=0, le=10)
    likes_count: int
    dislikes_count: int
    timestamp: datetime


class BookmarkResponse(BaseModel):
    id: str
    user_id: UUID
    film_id: UUID
    timestamp: datetime


class SearchRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None
    skip: int = 0
    limit: int = 10
    sort_by: Optional[str] = None
    sort_order: int = 1
