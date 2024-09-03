from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from genre import Genre
from person import Person


class Film(BaseModel):
    id: UUID
    title: str
    rating: float


class FilmDetail(Film):
    type: str
    description: Optional[str] = None
    genres: list[Genre] = []
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []
