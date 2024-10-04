from uuid import UUID

from pydantic import BaseModel

from movie_service.src.models.genre import Genre
from movie_service.src.models.person import Person


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
