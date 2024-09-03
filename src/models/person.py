from pydantic import BaseModel
from uuid import UUID
from enum import StrEnum


class Roles(StrEnum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'


class PersonFilm(BaseModel):
    film_id: UUID
    roles: list[Roles]


class Person(BaseModel):
    id: UUID
    full_name: str


class PersonFilmsParticipant(Person):
    films: list[PersonFilm]
