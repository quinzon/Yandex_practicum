from functools import lru_cache
from typing import List, Type, Tuple

from fastapi import Depends
from sqlalchemy import select, func
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

    async def get_login_history(
            self,
            user_id: str,
            page_size: int,
            page_number: int
    ) -> Tuple[List[LoginHistory], int]:
        total_query = select(func.count()).where(LoginHistory.user_id == user_id)
        total_result = await self.session.execute(total_query)
        total_items = total_result.scalar_one()

        query = (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.timestamp.desc())
            .offset((page_number - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        items = result.scalars().all()

        return items, total_items


@lru_cache()
def get_login_history_repository(
        session: AsyncSession = Depends(get_session)
) -> LoginHistoryRepository:
    return LoginHistoryRepository(session)
