from uuid import UUID

from pydantic import BaseModel

from src.models.genre import Genre
from src.models.person import Person


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
