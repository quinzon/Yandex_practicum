from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from ugc_service.src.core.exceptions import DuplicateException
from ugc_service.src.core.utils import has_permission
from ugc_service.src.models.models import FilmAggregatedRatingResponse, FilmRatingResponse, \
    FilmRatingCreate
from ugc_service.src.services.film_rating import FilmRatingService, get_film_rating_service

router = APIRouter(dependencies=[Depends(has_permission)])


@router.post('/ratings', response_model=FilmRatingResponse)
async def create_rating(
        rating: FilmRatingCreate,
        service: FilmRatingService = Depends(get_film_rating_service)
):
    try:
        return await service.create_rating(rating)
    except DuplicateException:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='FilmRating with this user_id and film_id already exists'
        )


@router.get('/ratings/{rating_id}', response_model=FilmRatingResponse)
async def get_rating(
        rating_id: str,
        service: FilmRatingService = Depends(get_film_rating_service)
):
    rating = await service.get_rating(rating_id)
    if not rating:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Rating not found')
    return rating


@router.delete('/ratings/{rating_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_rating(
        rating_id: str,
        service: FilmRatingService = Depends(get_film_rating_service)
):
    await service.delete_rating(rating_id)
    return {'message': 'Rating deleted successfully'}


@router.get('/ratings/{film_id}/average', response_model=FilmAggregatedRatingResponse)
async def get_average_rating(
        film_id: str,
        service: FilmRatingService = Depends(get_film_rating_service)
):
    return await service.get_average_rating(film_id)
