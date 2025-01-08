from beanie import Document
from pydantic import Field
from datetime import datetime


class Bookmark(Document):
    user_id: str
    film_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'bookmarks'
        indexes = [
            [('user_id', 1), ('film_id', 1)],
        ]


class Review(Document):
    user_id: str
    film_id: str
    review_text: str = Field(..., max_length=500)
    rating: int = Field(..., ge=0, le=10)
    likes: set[str] = Field(default_factory=list)
    dislikes: set[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'reviews'
        indexes = [
            [('user_id', 1), ('film_id', 1)]
        ]


class FilmRating(Document):
    user_id: str
    film_id: str
    rating: int = Field(..., ge=0, le=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = 'film_ratings'
        indexes = [
            [('user_id', 1), ('film_id', 1)]
        ]
