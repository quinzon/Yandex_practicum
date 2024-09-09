import json
from functools import lru_cache
from typing import Optional, List
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException, Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film
from src.models.person import PersonFilmsParticipant, Person, PersonFilm, Roles
from src.services.film import FilmService, get_film_service

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    SORTABLE_FIELDS = {
        "full_name": "full_name.keyword"
    }

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, film_service: FilmService):
        self.elastic = elastic
        self.redis = redis
        self.film_service = film_service

    async def get_person_by_id(self, person_id: UUID) -> Optional[PersonFilmsParticipant]:
        """
        Get a person by their ID, including their films and roles.
        """
        cache_key = f"person:{person_id}"
        cached_data = await self._get_single_person_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.elastic.get(index='persons', id=str(person_id))
            person_data = response['_source']
            person = PersonFilmsParticipant(id=person_data['id'], full_name=person_data['full_name'], films=[])

            films_data = await self.film_service.get_films_by_person_id(person_id)

            person.films = self._process_film_roles(films_data, person_id)

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
            page_size: int = 50,
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
        return await self._fetch_persons(page_size=page_size, page_number=page_number, sort=sort,
                                         search_body=search_body)

    async def get_person_films(self, person_id: UUID, page_size: int = 50, page_number: int = 1,
                               sort: Optional[str] = "-imdb_rating") -> List[Film]:
        """
        Get all films associated with a person by their ID, with pagination and sorting.
        """
        from_ = (page_number - 1) * page_size

        films_data = await self.film_service.get_films_by_person_id(person_id, from_=from_, size=page_size, sort=sort)

        films = []
        for person_film in films_data:
            film = await self.film_service.get_by_id(str(person_film['_id']))
            if film:
                films.append(film)

        return films

    def _process_film_roles(self, films_data: List[dict], person_id: UUID) -> List[PersonFilm]:
        """
        Process raw film data and determine the roles of the person in each film (actor, writer, director).
        """
        films = []
        for hit in films_data:
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

    async def _get_person_films_data(self, films_data: List[dict]) -> List[PersonFilm]:
        """
        Helper method to fetch film data using FilmService.
        """
        films = []
        for film_data in films_data:
            film_id = film_data.get('film_id')
            if film_id:
                film = await self.film_service.get_by_id(film_id)
                if film:
                    person_film = PersonFilm(film_id=film.id, roles=film_data.get('roles', []))
                    films.append(person_film)
        return films

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
        elastic: AsyncElasticsearch = Depends(get_elastic),
        film_service: FilmService = Depends(get_film_service)
) -> PersonService:
    return PersonService(redis, elastic, film_service)
