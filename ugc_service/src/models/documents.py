from beanie import Document
from pydantic import Field
from uuid import UUID
from datetime import datetime


class Bookmark(Document):
    user_id: UUID
    film_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'bookmarks'
        indexes = [
            {'fields': ['user_id', 'film_id'], 'unique': True}
        ]


class Review(Document):
    user_id: UUID
    film_id: UUID
    review_text: str = Field(..., max_length=500)
    rating: int = Field(..., ge=0, le=10)
    likes: list[UUID] = Field(default_factory=list)
    dislikes: list[UUID] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'reviews'
        indexes = [
            {'fields': ['user_id', 'film_id'], 'unique': True}
        ]


class FilmRating(Document):
    user_id: UUID
    film_id: UUID
    rating: int = Field(..., ge=0, le=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'film_ratings'
        indexes = [
            {'fields': ['user_id', 'film_id'], 'unique': True}
        ]
