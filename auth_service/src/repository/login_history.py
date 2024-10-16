from functools import lru_cache
from typing import List, Type

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.login_history import LoginHistory
from auth_service.src.repository.base import BaseRepository


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def get_model(self) -> Type[LoginHistory]:
        return LoginHistory

    async def save_login_history(self, login_history: LoginHistory) -> None:
        self.session.add(login_history)
        await self.session.commit()

    async def get_login_history(self, user_id: str) -> List[LoginHistory] | None:
        query = select(LoginHistory).where(LoginHistory.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()


@lru_cache()
def get_login_history_repository(
    session: AsyncSession = Depends(get_session)
) -> LoginHistoryRepository:
    return LoginHistoryRepository(session)
