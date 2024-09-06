import json
from functools import lru_cache
from typing import Optional, List
from uuid import UUID

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException, Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import PersonFilmsParticipant, Person, PersonFilm

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    SORTABLE_FIELDS = {
        "full_name": "full_name.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.redis = redis

    async def get_person_by_id(self, person_id: UUID) -> Optional[PersonFilmsParticipant]:
        """
        Get a person by their ID, including their films and roles. The result will be cached if found.
        """
        cache_key = f"person:{person_id}"
        cached_data = await self._get_single_person_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.get(index='persons', id=str(person_id))
            person_data = response['_source']
            films = [PersonFilm(**film) for film in person_data.get('films', [])]
            person = PersonFilmsParticipant(id=person_data['id'], full_name=person_data['full_name'], films=films)
            await self._put_single_person_to_cache(cache_key, person)
            return person
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Person not found: {str(e)}")

    async def get_all_persons(
            self,
            page_size: int = 10,
            page_number: int = 1,
            sort: Optional[str] = None
    ) -> List[Person]:
        """
        Get a list of persons with pagination and sorting.
        """
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort)

    async def search_persons(
            self,
            query: str,
            page_size: int = 10,
            page_number: int = 1,
            sort: Optional[str] = None
    ) -> List[Person]:
        """
        Search for persons based on a query string with pagination and sorting.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["full_name^3"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort, search_body=search_body)

    async def get_person_films(self, person_id: UUID) -> List[PersonFilm]:
        """
        Get all films associated with a person by their ID, including roles in the films.
        """
        person = await self.get_person_by_id(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person.films

    async def _fetch_persons(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str] = None,
            search_body: Optional[dict] = None
    ) -> List[Person]:
        """
        Helper method to fetch persons from Elasticsearch with pagination, sorting, and optional search.
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
            "query": search_body if search_body else {"match_all": {}},
            "sort": [{sort_field: {"order": sort_order}}] if sort_field else []
        }

        cache_key_parts = [f"persons:list:{page_number}:{page_size}:{sort}"]
        if search_body:
            cache_key_parts.append(str(search_body))
        cache_key = ":".join(cache_key_parts)

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.search(index='persons', body=body)
            persons = [Person(**doc['_source']) for doc in response['hits']['hits']]

            await self._put_to_cache(cache_key, persons)

            return persons
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Elasticsearch error: {str(e)}")

    async def _get_from_cache(self, cache_key: str) -> Optional[List[Person]]:
        """
        Retrieve data from Redis cache.
        """
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return [Person.parse_raw(item) for item in json.loads(cached_data)]
        return None

    async def _put_to_cache(self, cache_key: str, data: List[Person]) -> None:
        """
        Store data in Redis cache.
        """
        serialized_data = json.dumps([person.json() for person in data])
        await self.redis.set(cache_key, serialized_data, ex=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _get_single_person_from_cache(self, cache_key: str) -> Optional[PersonFilmsParticipant]:
        """
        Retrieve a single person from Redis cache.
        """
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return PersonFilmsParticipant.parse_raw(cached_data)
        return None

    async def _put_single_person_to_cache(self, cache_key: str, person: PersonFilmsParticipant) -> None:
        """
        Store a single person in Redis cache.
        """
        await self.redis.set(cache_key, person.json(), ex=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(redis, elastic)
