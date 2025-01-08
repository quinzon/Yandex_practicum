from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus

from ugc_service.src.core.utils import has_permission
from ugc_service.src.models.documents import Bookmark
from ugc_service.src.models.models import SearchRequest, PaginatedResponse, BookmarkResponse, BookmarkRequest
from ugc_service.src.services.bookmark import BookmarkService, get_bookmark_service

router = APIRouter(dependencies=[Depends(has_permission)])


@router.post('/bookmarks', response_model=Bookmark)
async def create_bookmark(
        bookmark_request: BookmarkRequest,
        user_id: str = Depends(has_permission),
        service: BookmarkService = Depends(get_bookmark_service)
):
    bookmark = Bookmark(film_id=bookmark_request.film_id, user_id=user_id)
    return await service.create_bookmark(bookmark)


@router.get('/bookmarks/{bookmark_id}', response_model=Bookmark)
async def get_bookmark(
        bookmark_id: str,
        service: BookmarkService = Depends(get_bookmark_service)
):
    bookmark = await service.get_bookmark(bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Bookmark not found')
    return bookmark


@router.delete('/bookmarks/{bookmark_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_bookmark(
        bookmark_id: str,
        service: BookmarkService = Depends(get_bookmark_service)
):
    await service.delete_bookmark(bookmark_id)
    return {'message': 'Bookmark deleted successfully'}


@router.post('/bookmarks/search', response_model=PaginatedResponse[BookmarkResponse])
async def search_bookmarks(
        request: SearchRequest,
        service: BookmarkService = Depends(get_bookmark_service)
):
    filters = request.filters or {}
    sort_params = {request.sort_by: request.sort_order} if request.sort_by else None
    return await service.search_bookmarks(filters, request.skip, request.limit, sort_params)
