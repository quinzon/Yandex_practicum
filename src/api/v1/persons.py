from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import Film
from src.models.person import Person, PersonFilmsParticipant
from src.models.pagination import Pagination, paginated_response
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get("/{person_id}", response_model=PersonFilmsParticipant, summary="Get Person by ID")
async def get_person_by_id(person_id: UUID, person_service: PersonService = Depends(get_person_service)):
    """
    Retrieve a person by their unique ID, including their films and roles.
    """
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.get("/", response_model=Pagination[Person], summary="List Persons with Pagination and Sorting")
@paginated_response()
async def list_persons(
        page_size: int = Query(50, gt=0, description="Number of items per page"),
        page_number: int = Query(1, gt=0, description="The page number to retrieve"),
        sort: Optional[str] = Query(None, description="Field to sort by"),
        person_service: PersonService = Depends(get_person_service),
):
    """
    Retrieve a list of persons with pagination and optional sorting.
    """
    return await person_service.get_all_persons(page_size=page_size, page_number=page_number, sort=sort)


@router.get("/search/", response_model=Pagination[Person], summary="Search Persons")
@paginated_response()
async def search_persons(
        query: str = Query(..., description="Search query"),
        page_size: int = Query(50, gt=0, description="Number of items per page"),
        page_number: int = Query(1, gt=0, description="The page number to retrieve"),
        sort: Optional[str] = Query(None, description="Field to sort by"),
        person_service: PersonService = Depends(get_person_service),
):
    """
    Search for persons by query string with pagination and optional sorting.
    """
    return await person_service.search_persons(query=query, page_size=page_size, page_number=page_number, sort=sort)


@router.get("/{person_id}/film/", response_model=Pagination[Film], summary="Get Films by Person ID")
@paginated_response()
async def get_person_films(
        person_id: UUID,
        page_size: int = Query(50, gt=0),
        page_number: int = Query(1, gt=0),
        sort: Optional[str] = Query("-imdb_rating", description="Sort by field"),
        person_service: PersonService = Depends(get_person_service)
):
    """
    Retrieve all films associated with a person by their ID, with pagination and sorting.
    """
    return await person_service.get_person_films(person_id, page_size=page_size, page_number=page_number, sort=sort)
