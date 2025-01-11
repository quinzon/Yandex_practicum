from functools import lru_cache
from typing import Optional

from fastapi import Depends

from ugc_service.src.models.documents import FilmRating
from ugc_service.src.models.models import FilmAggregatedRatingResponse, FilmRatingResponse, \
    FilmRatingCreate
from ugc_service.src.repository.film_rating import FilmRatingRepository, get_film_rating_repository


class FilmRatingService:
    def __init__(self, repository: FilmRatingRepository):
        self.repository = repository

    async def create_rating(self, rating_data: FilmRatingCreate) -> FilmRatingResponse:
        film_rating_doc = FilmRating(
            user_id=rating_data.user_id,
            film_id=rating_data.film_id,
            rating=rating_data.rating,
        )
        film_rating_doc = await self.repository.create(film_rating_doc)
        return FilmRatingResponse(
            user_id=film_rating_doc.user_id,
            film_id=film_rating_doc.film_id,
            rating=film_rating_doc.rating,
            timestamp=film_rating_doc.timestamp,
        )

    async def get_rating(self, rating_id: str) -> Optional[FilmRatingResponse]:
        doc = await self.repository.get(rating_id)
        if not doc:
            return None
        return FilmRatingResponse(
            user_id=doc.user_id,
            film_id=doc.film_id,
            rating=doc.rating,
            timestamp=doc.timestamp,
        )

    async def update_rating(
            self, rating_id: str, rating_data: FilmRatingCreate
    ) -> Optional[FilmRatingResponse]:
        existing_doc = await self.repository.get(rating_id)
        if not existing_doc:
            return None
        existing_doc.user_id = rating_data.user_id
        existing_doc.film_id = rating_data.film_id
        existing_doc.rating = rating_data.rating
        updated_doc = await self.repository.update(rating_id, existing_doc)
        if not updated_doc:
            return None
        return FilmRatingResponse(
            user_id=updated_doc.user_id,
            film_id=updated_doc.film_id,
            rating=updated_doc.rating,
            timestamp=updated_doc.timestamp,
        )

    async def delete_rating(self, rating_id: str) -> None:
        await self.repository.delete(rating_id)

    async def get_average_rating(self, film_id: str) -> FilmAggregatedRatingResponse:
        return await self.repository.get_average_rating(film_id)


@lru_cache()
def get_film_rating_service(
        repository: FilmRatingRepository = Depends(get_film_rating_repository)
) -> FilmRatingService:
    return FilmRatingService(repository)
