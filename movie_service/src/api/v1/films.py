from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from movie_service.src.models.film import FilmDetail, Permissions
from movie_service.src.services.auth import AuthService, get_auth_service
from movie_service.src.services.film import FilmService, get_film_service
from movie_service.src.models.pagination import Pagination, paginated_response


router = APIRouter()


@router.get("/search", response_model=Pagination[FilmDetail], summary="Search Films with Pagination and Sorting")
@paginated_response()
async def search_films(
    query: str = Query(..., description="Search films"),
    page_size: int = Query(50, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: str | None = Query(None, description="Field to sort by"),
    film_service: FilmService = Depends(get_film_service),
):
    """
    Search for films by query string with pagination and optional sorting.
    """
    return await film_service.search(query=query, page_size=page_size, page_number=page_number, sort=sort)


@router.get('/{film_id}', response_model=FilmDetail)
async def film_details(
    film_id: UUID,
    request: Request,
    film_service: FilmService = Depends(get_film_service),
    auth_service: AuthService = Depends(get_auth_service)
) -> FilmDetail:
    """
    Get film details by film_id.
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Film not found")

    if film.permission is Permissions.PUBLIC:
        return film

    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Authorization token missing"
        )

    await auth_service.check_permission(token, f'film:{film.permission.value}', "GET")

    return film


@router.get('', response_model=Pagination[FilmDetail], summary="List Films with Pagination and Sorting")
@paginated_response()
async def list_films(
    page_size: int = Query(50, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: str | None = Query(None, description="Field to sort by"),
    film_service: FilmService = Depends(get_film_service),
):
    """
    Retrieve a list of films with pagination and optional sorting.
    """
    return await film_service.get_all(page_size=page_size, page_number=page_number, sort=sort)
