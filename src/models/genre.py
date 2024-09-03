from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class GenreFilm(BaseModel):
    film_id: UUID


class Genre(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None


class GenreFilmsOverlap(Genre):
    films: list[GenreFilm]
