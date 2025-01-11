from functools import lru_cache
from typing import Type
from ugc_service.src.models.documents import FilmRating
from ugc_service.src.models.models import FilmAggregatedRatingResponse
from ugc_service.src.repository.base import BaseRepository


class FilmRatingRepository(BaseRepository[FilmRating]):
    def get_model(self) -> Type[FilmRating]:
        return FilmRating

    async def get_average_rating(self, film_id: str) -> FilmAggregatedRatingResponse:
        pipeline = [
            {'$match': {'film_id': film_id}},
            {
                '$group': {
                    '_id': '$film_id',
                    'avg_rating': {'$avg': '$rating'},
                    'total_ratings': {'$sum': 1},
                }
            }
        ]
        result = await FilmRating.aggregate(pipeline).to_list()

        if not result:
            return FilmAggregatedRatingResponse(
                film_id=film_id,
                avg_rating=0.0,
                total_ratings=0,
            )

        doc = result[0]
        return FilmAggregatedRatingResponse(
            film_id=film_id,
            avg_rating=doc['avg_rating'],
            total_ratings=doc['total_ratings'],
        )

@lru_cache()
def get_film_rating_repository() -> FilmRatingRepository:
    return FilmRatingRepository()
