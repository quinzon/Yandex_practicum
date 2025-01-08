from functools import lru_cache
from typing import Optional

from fastapi import Depends

from ugc_service.src.models.documents import FilmRating
from ugc_service.src.repository.film_rating import FilmRatingRepository, get_film_rating_repository


class FilmRatingService:
    def __init__(self, repository: FilmRatingRepository):
        self.repository = repository

    async def create_rating(self, rating: FilmRating) -> FilmRating:
        return await self.repository.create(rating)

    async def get_rating(self, rating_id: str) -> Optional[FilmRating]:
        return await self.repository.get(rating_id)

    async def update_rating(self, rating_id: str, rating: FilmRating) -> Optional[FilmRating]:
        return await self.repository.update(rating_id, rating)

    async def delete_rating(self, rating_id: str) -> None:
        await self.repository.delete(rating_id)

    async def get_average_rating(self, film_id: str) -> float:
        return await self.repository.get_average_rating(film_id)


@lru_cache()
def get_film_rating_service(
        repository: FilmRatingRepository = Depends(get_film_rating_repository)
) -> FilmRatingService:
    return FilmRatingService(repository)
