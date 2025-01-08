from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus

from ugc_service.src.core.utils import has_permission
from ugc_service.src.models.documents import Review
from ugc_service.src.models.models import SearchRequest, PaginatedResponse, ReviewResponse, ReactionRequest, \
    ReactionType
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


@router.post('/reviews', response_model=Review)
async def create_review(
        review: Review,
        service: ReviewService = Depends(get_review_service)
):
    return await service.create_review(review)


@router.get('/reviews/{review_id}', response_model=Review)
async def get_review(
        review_id: str,
        service: ReviewService = Depends(get_review_service)
):
    review = await service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')
    return review


@router.put('/reviews/{review_id}', response_model=Review)
async def update_review(
        review_id: str,
        review: Review,
        service: ReviewService = Depends(get_review_service)
):
    updated_review = await service.update_review(review_id, review)
    if not updated_review:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')
    return updated_review


@router.delete('/reviews/{review_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_review(
        review_id: str,
        service: ReviewService = Depends(get_review_service)
):
    await service.delete_review(review_id)
    return {'message': 'Review deleted successfully'}


@router.patch('/reviews/{review_id}/reaction', status_code=HTTPStatus.NO_CONTENT)
async def react_to_review(
        reaction: ReactionRequest,
        review_id: str,
        user_id: str = Depends(has_permission),
        service: ReviewService = Depends(get_review_service)
):
    review = await service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Review not found')

    if reaction.reaction == ReactionType.like:
        if user_id in review.likes:
            review.likes.remove(user_id)
        else:
            review.likes.add(user_id)
            review.dislikes.discard(user_id)
    elif reaction.reaction == ReactionType.dislike:
        if user_id in review.dislikes:
            review.dislikes.remove(user_id)
        else:
            review.dislikes.add(user_id)
            review.likes.discard(user_id)

    await service.update_review(review_id, review)
    return {'message': f'{reaction.reaction.capitalize()} toggled successfully'}
