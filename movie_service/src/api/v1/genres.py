import http
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from movie_service.src.models.film import Film
from movie_service.src.services.genre import GenreService, get_genre_service
from movie_service.src.models.genre import Genre
from movie_service.src.models.pagination import Pagination, paginated_response

router = APIRouter()


@router.get("/search", response_model=Pagination[Genre], summary="Search Genres with Pagination and Sorting")
@paginated_response()
async def search_genres(
    query: str = Query(..., description="Search query"),
    page_size: int = Query(50, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: str | None = Query(None, description="Field to sort by"),
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Search for genres by query string with pagination and optional sorting.
    """
    return await genre_service.search(query=query, page_size=page_size, page_number=page_number, sort=sort)


@router.get("/{genre_id}", response_model=Genre, summary="Get Genre by ID")
async def get_genre_by_id(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)):
    """
    Retrieve a genre by its unique ID.
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Genre not found")
    return genre


@router.get("/", response_model=Pagination[Genre], summary="List Genres with Pagination and Sorting")
@paginated_response()
async def list_genres(
    page_size: int = Query(50, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: str | None = Query(None, description="Field to sort by"),
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Retrieve a list of genres with pagination and optional sorting.
    """
    return await genre_service.get_all(page_size=page_size, page_number=page_number, sort=sort)


@router.get("/{genre_id}/film/", response_model=Pagination[Film], summary="Get Films by Genre ID")
@paginated_response()
async def get_genre_films(
    genre_id: UUID,
    page_size: int = Query(50, gt=0),
    page_number: int = Query(1, gt=0),
    sort: str | None = Query("-imdb_rating", description="Sort by field"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Retrieve all films associated with a genre by genre ID, with pagination and sorting.
    """
    return await genre_service.get_genre_films(genre_id, page_size=page_size, page_number=page_number, sort=sort)
