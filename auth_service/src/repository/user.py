from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.user import User, user_role
from auth_service.src.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def get_model(self) -> Type[User]:
        return User

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).options(selectinload(User.roles)).filter(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def assign_role(self, user_id: str, role_id: str) -> None:
        query = insert(user_role).values(user_id=user_id, role_id=role_id)
        await self.session.execute(query)
        await self.session.commit()


@lru_cache()
def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)
