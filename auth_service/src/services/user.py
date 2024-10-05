from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from auth_service.src.models.dto.user import UserCreate
from auth_service.src.models.entities.user import User


async def create_user(user_data: UserCreate, session: AsyncSession) -> User:
    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    new_user.set_password(user_data.password)
    session.add(new_user)

    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
