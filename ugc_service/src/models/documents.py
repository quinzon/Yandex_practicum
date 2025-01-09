from datetime import datetime
from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

class Bookmark(Document):
    user_id: str
    film_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = 'bookmarks'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('film_id', ASCENDING)],
                unique=True
            )
        ]

class Review(Document):
    user_id: str
    film_id: str
    review_text: str = Field(..., max_length=500)
    rating: int = Field(..., ge=0, le=10)
    likes: set[str] = Field(default_factory=set)
    dislikes: set[str] = Field(default_factory=set)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = 'reviews'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('film_id', ASCENDING)],
                unique=True
            )
        ]

class FilmRating(Document):
    user_id: str
    film_id: str
    rating: int = Field(..., ge=0, le=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = 'film_ratings'
        indexes = [
            IndexModel(
                [('user_id', ASCENDING), ('film_id', ASCENDING)],
                unique=True
            )
        ]
