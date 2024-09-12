from pydantic import BaseModel
from uuid import UUID


class GenreFilm(BaseModel):
    film_id: UUID


class Genre(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class GenreFilmsOverlap(Genre):
    films: list[GenreFilm]
