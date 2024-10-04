from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.dto.user import UserResponse, UserCreate
from auth_service.src.services.user import create_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Register new user
    """
    user = await create_user(user_data, session)
    return user
