from functools import lru_cache
from typing import Type
from ugc_service.src.models.documents import FilmRating
from ugc_service.src.repository.base import BaseRepository


class FilmRatingRepository(BaseRepository[FilmRating]):
    def get_model(self) -> Type[FilmRating]:
        return FilmRating

    async def get_average_rating(self, film_id: str) -> float:
        ratings = await FilmRating.find({'film_id': film_id}).aggregate([
            {'$group': {'_id': None, 'average': {'$avg': '$rating'}}}
        ]).to_list()

        if ratings:
            return ratings[0]['average']
        return 0.0


@lru_cache()
def get_film_rating_repository() -> FilmRatingRepository:
    return FilmRatingRepository()
