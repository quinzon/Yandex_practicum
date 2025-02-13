from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from ugc_service.src.core.exceptions import DuplicateException
from ugc_service.src.core.utils import has_permission
from ugc_service.src.models.models import SearchRequest, PaginatedResponse, ReviewResponse, \
    ReactionRequest, ReviewCreate, ReviewUpdate
from ugc_service.src.services.review import ReviewService, get_review_service

router = APIRouter(dependencies=[Depends(has_permission)])


@router.post('/reviews/search', response_model=PaginatedResponse[ReviewResponse])
async def search_reviews(
        request: SearchRequest,
        service: ReviewService = Depends(get_review_service)
):
    filters = request.filters or {}
    sort_params = {request.sort_by: request.sort_order} if request.sort_by else None
    return await service.search_reviews(filters, request.skip, request.limit, sort_params)


@router.get('/reviews/users/{user_id}', response_model=PaginatedResponse[ReviewResponse])
async def get_user_bookmarks(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, le=50),
        sort_by: str = Query(None),
        sort_order: int = Query(1),
        service: ReviewService = Depends(get_review_service)  # noqa: WPS211
):
    filters = {'user_id': user_id}
    sort_params = {sort_by: sort_order} if sort_by else None
    return await service.search_reviews(filters, skip, limit, sort_params)


@router.post('/reviews', response_model=ReviewResponse)
async def create_review(
        data: ReviewCreate,
        service: ReviewService = Depends(get_review_service)
):
    try:
        return await service.create_review(data)
    except DuplicateException:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Review with this user_id and film_id already exists'
        )


@router.get('/reviews/{review_id}', response_model=ReviewResponse)
async def get_review(
        review_id: str,
        service: ReviewService = Depends(get_review_service)
):
    review = await service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')
    return review


@router.put('/reviews/{review_id}', response_model=ReviewResponse)
async def update_review(
        review_id: str,
        data: ReviewUpdate,
        service: ReviewService = Depends(get_review_service)
):
    updated = await service.update_review(review_id, data)
    if not updated:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')
    return updated


@router.delete('/reviews/{review_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_review(
        review_id: str,
        service: ReviewService = Depends(get_review_service)
):
    await service.delete_review(review_id)
    return {'message': 'Review deleted successfully'}


@router.patch('/reviews/{review_id}/reaction', status_code=HTTPStatus.NO_CONTENT)
async def react_to_review(
        review_id: str,
        reaction: ReactionRequest,
        user_id: str = Depends(has_permission),
        service: ReviewService = Depends(get_review_service)
):
    found = await service.toggle_reaction(review_id, user_id, reaction.reaction)
    if not found:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')

    return {'message': f'{reaction.reaction.capitalize()} toggled successfully'}
