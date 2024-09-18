from abc import ABC, abstractmethod
from typing import Tuple, List
from uuid import UUID

from src.models.genre import Genre
from src.models.film import FilmDetail, Film
from src.models.person import Person, PersonFilmsParticipant


class ApiServiceInterface(ABC):

    @abstractmethod
    async def get_by_id(self, film_id: UUID) -> FilmDetail | Film | Genre | Person | PersonFilmsParticipant | None:
        pass

    @abstractmethod
    async def get_all(
            self,
            page_size: int,
            page_number: int,
            sort: str | None
    ) -> Tuple[List[FilmDetail | Film | Genre], int]:
        pass


class SearchableApiServiceInterface(ApiServiceInterface):
    @abstractmethod
    async def search(
            self,
            query: str,
            page_size: int,
            page_number: int,
            sort: str | None
    ) -> Tuple[List[FilmDetail | Film | Genre], int]:
        pass
