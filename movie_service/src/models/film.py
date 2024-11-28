from uuid import UUID
from enum import Enum

from pydantic import BaseModel

from movie_service.src.models.genre import Genre
from movie_service.src.models.person import Person


class Permissions(str, Enum):
    PUBLIC = 'public'
    SUBSCRIPTION = 'subscription'
    CLOSED = 'closed'


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


class FilmDetail(Film):
    description: str | None = None
    genres: list[Genre] = []
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []
    permission: Permissions
