import http
from functools import lru_cache
from typing import List, Tuple
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException, Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film
from src.models.person import PersonFilmsParticipant, Person, PersonFilm, Roles
from src.services.cache import CacheService
from src.services.film import FilmService, get_film_service


class PersonService(CacheService):
    SORTABLE_FIELDS = {
        "full_name": "full_name.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, film_service: FilmService):
        super().__init__(redis)
        self.elastic = elastic
        self.film_service = film_service

    async def get_person_by_id(self, person_id: UUID) -> PersonFilmsParticipant | None:
        """
        Get a person by their ID, including their films and roles.
        """
        cache_key = f"person:{person_id}"
        cached_data = await self._get_from_cache_by_id(cache_key, PersonFilmsParticipant)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.get(index='persons', id=str(person_id))
            person_data = response['_source']
            person = PersonFilmsParticipant(id=person_data['id'], full_name=person_data['full_name'], films=[])

            films_data, total_items = await self.film_service.get_films_by_person_id(person_id)
            person.films = self._process_film_roles(films_data, person_id)

            await self._put_to_cache_by_id(cache_key, person)
            return person
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Exception occurred: {str(e)}")

    async def get_all_persons(
            self,
            page_size: int = 10,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Person], int]:
        """
        Get a list of persons with pagination, sorting, and total count.
        """
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort)

    async def search_persons(
            self,
            query: str,
            page_size: int = 50,
            page_number: int = 1,
            sort: str | None = None
    ) -> Tuple[List[Person], int]:
        """
        Search for persons based on a query string with pagination, sorting, and total count.
        """
        search_body = {
            "multi_match": {
                "query": query,
                "fields": ["full_name^3"],
                "fuzziness": "AUTO"
            }
        }
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort,
                                         search_body=search_body)

    async def get_person_films(self, person_id: UUID, page_size: int = 50, page_number: int = 1,
                               sort: str | None = "-imdb_rating") -> tuple[list[Film], int]:
        """
        Get all films associated with a person by their ID, with pagination and sorting.
        """
        from_ = (page_number - 1) * page_size
        films_data, total_items = await self.film_service.get_films_by_person_id(person_id, from_=from_, size=page_size,
                                                                                 sort=sort)

        films = []
        for person_film in films_data:
            film = await self.film_service.get_film_by_id(str(person_film['_id']))
            if film:
                films.append(film)

        return films, total_items

    @staticmethod
    def _process_film_roles(films_data: List[dict], person_id: UUID) -> List[PersonFilm]:
        """
        Process raw film data and determine the roles of the person in each film (actor, writer, director).
        """
        films = []
        for hit in films_data:
            print(hit)
            film_id = hit['_id']
            source = hit['_source']

            roles = []
            if any(actor['id'] == str(person_id) for actor in source.get('actors', [])):
                roles.append(Roles.ACTOR)
            if any(writer['id'] == str(person_id) for writer in source.get('writers', [])):
                roles.append(Roles.WRITER)
            if any(director['id'] == str(person_id) for director in source.get('directors', [])):
                roles.append(Roles.DIRECTOR)

            person_film = PersonFilm(film_id=UUID(film_id), roles=roles)
            films.append(person_film)

        return films

    async def _fetch_persons(
            self,
            page_size: int,
            page_number: int,
            sort: str | None = None,
            search_body: dict | None = None
    ) -> Tuple[List[Person], int]:
        """
        Helper method to fetch persons from Elasticsearch with pagination, sorting, total count, and caching.
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

        cached_data = await self._get_list_from_cache(cache_key, Person)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.search(index='persons', body=body)
            persons = [Person(**doc['_source']) for doc in response['hits']['hits']]
            total_items = response['hits']['total']['value']

            await self._put_list_to_cache(cache_key, persons, total_items)

            return persons, total_items
        except Exception as e:
            raise HTTPException(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Elasticsearch error: {str(e)}")


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        film_service: FilmService = Depends(get_film_service)
) -> PersonService:
    return PersonService(redis, elastic, film_service)
