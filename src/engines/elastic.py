import uuid
from typing import Tuple, List

from elasticsearch import AsyncElasticsearch

from src.engines.base import AsyncSearchEngine


class ElasticAsyncSearchEngine(AsyncSearchEngine):

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index: str, _id: uuid) -> dict:
        response = await self.elastic.get(index=index, id=str(_id))
        return response['_source']

    async def get_list(
            self,
            index: str,
            page_size: int,
            page_number: int,
            sort_order: str | None = None,
            sort_field: str | None = None,
            query: str | None = None,
    ) -> Tuple[List, int]:

        from_ = (page_number - 1) * page_size

        body = {
            "from": from_,
            "size": page_size,
            "query": query if query else {"match_all": {}},
            "sort": [{sort_field: {"order": sort_order}}] if sort_field else []
        }

        response = await self.elastic.search(index=index, body=body)
        return response['hits']['hits'], response['hits']['total']['value']
