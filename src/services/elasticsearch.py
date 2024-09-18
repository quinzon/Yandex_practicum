from typing import Tuple, List, Type, Union
from uuid import UUID

from elasticsearch import AsyncElasticsearch

from src.models.film import FilmDetail, Film
from src.models.genre import Genre
from src.models.person import Person, PersonFilmsParticipant


class ElasticsearchService:
    SORTABLE_FIELDS = {
        "imdb_rating": "imdb_rating",
        "title": "title.raw",
        "full_name": "full_name.raw"
    }

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def _gather_request_body(
            self,
            page_size: int,
            page_number: int,
            sort: str | None = None,
            query: dict | None = None
    ) -> dict:
        """
        Forms the request body in Elasticsearch, includes sorting, pagination, custom query.
        """
        from_ = (page_number - 1) * page_size

        sort_order = "asc"
        if sort and sort.startswith('-'):
            sort_order = "desc"
            sort = sort[1:]

        sort_field = self.SORTABLE_FIELDS.get(sort, sort)

        body = {
            "from": from_,
            "size": page_size,
            "query": query if query else {"match_all": {}},
            "sort": [{sort_field: {"order": sort_order}}] if sort_field else []
        }
        return body

    async def _response_list(
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
        body = await self._gather_request_body(page_size, page_number, sort, query)

        response = await self.elastic.search(index=index, body=body)
        data = [model(**doc['_source']) for doc in response['hits']['hits']]
        total_items = response['hits']['total']['value']
        return data, total_items

    async def _response_by_id(
            self,
            index: str,
            uuid: UUID,
            model: Type[Union[FilmDetail, Film, Genre, Person]]
    ) -> FilmDetail | Film | Genre | Person | PersonFilmsParticipant:
        """
        Retrieves data by id from Elasticsearch.
        """
        response = await self.elastic.get(index=index, id=str(uuid))
        return model(**response['_source'])
