from enum import Enum
from typing import List, TypeVar, Generic, Optional, Dict, Any

from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: List[T]


class FilmRatingResponse(BaseModel):
    user_id: str
    film_id: str
    rating: int = Field(..., ge=0, le=10)
    timestamp: datetime


class FilmAggregatedRatingResponse(BaseModel):
    film_id: str
    avg_rating: float
    likes_count: int
    dislikes_count: int
    total_ratings: int


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    film_id: str
    review_text: str
    rating: int = Field(..., ge=0, le=10)
    likes_count: int
    dislikes_count: int
    timestamp: datetime


class BookmarkResponse(BaseModel):
    id: str
    user_id: str
    film_id: str
    timestamp: datetime


class BookmarkRequest(BaseModel):
    film_id: str


class SearchRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None
    skip: int = 0
    limit: int = 10
    sort_by: Optional[str] = None
    sort_order: int = 1


class ReactionType(str, Enum):
    like = "like"
    dislike = "dislike"


class ReactionRequest(BaseModel):
    reaction: ReactionType
