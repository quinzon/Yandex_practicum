from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from src.services.genre import GenreService, get_genre_service
from src.models.genre import Genre

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre, summary="Get Genre by ID")
async def get_genre_by_id(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)):
    """
    Retrieve a genre by its unique ID.
    """
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.get("/", response_model=List[Genre], summary="List Genres")
async def list_genres(
    page_size: int = Query(10, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: Optional[str] = Query(None, description="Field to sort by"),
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Retrieve a list of genres with pagination and optional sorting.
    """
    return await genre_service.get_all_genres(page_size=page_size, page_number=page_number, sort=sort)


@router.get("/search/", response_model=List[Genre], summary="Search Genres")
async def search_genres(
    query: str = Query(..., description="Search query"),
    page_size: int = Query(10, gt=0, description="Number of items per page"),
    page_number: int = Query(1, gt=0, description="The page number to retrieve"),
    sort: Optional[str] = Query(None, description="Field to sort by"),
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Search for genres by query string with pagination and optional sorting.
    """
    return await genre_service.search_genres(query=query, page_size=page_size, page_number=page_number, sort=sort)
