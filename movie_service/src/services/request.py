from functools import lru_cache
from typing import Tuple, List, Type, Union
from uuid import UUID

from fastapi import Depends

from movie_service.src.db.elastic import get_elastic_engine
from movie_service.src.engines.base import AsyncSearchEngine
from movie_service.src.models.film import FilmDetail, Film
from movie_service.src.models.genre import Genre
from movie_service.src.models.person import Person, PersonFilmsParticipant


class RequestService:
    SORTABLE_FIELDS = {
        "imdb_rating": "imdb_rating",
        "title": "title.raw",
        "full_name": "full_name.raw",
        "name": "name.raw"
    }

    def __init__(self, search_engine: AsyncSearchEngine):
        self.search_engine = search_engine

    async def response_list(
            self,
            index: str,
            model: Type[Union[FilmDetail, Film, Genre, Person]],
            page_size: int,
            page_number: int,
            sort: str | None = None,
            query: dict | None = None
    ) -> Tuple[List, int]:
        """
        Retrieves list of data from Elasticsearch.
        """

        sort_order = "asc"
        if sort and sort.startswith('-'):
            sort_order = "desc"
            sort = sort[1:]

        sort_field = self.SORTABLE_FIELDS.get(sort, sort)

        response, total_items = await self.search_engine.get_list(index, page_size, page_number, sort_order, sort_field, query)
        data = [model(**doc['_source']) for doc in response]
        return data, total_items

    async def response_by_id(
            self,
            index: str,
            uuid: UUID,
            model: Type[Union[FilmDetail, Film, Genre, Person]]
    ) -> FilmDetail | Film | Genre | Person | PersonFilmsParticipant:
        """
        Retrieves data by id from Elasticsearch.
        """
        obj = await self.search_engine.get_by_id(index, uuid)
        return model(**obj)


@lru_cache()
def get_request_service(
        elastic_engine: AsyncSearchEngine = Depends(get_elastic_engine)
) -> RequestService:
    return RequestService(elastic_engine)
