from functools import lru_cache
from typing import List
from uuid import UUID

from fastapi import Depends

from auth_service.src.models.entities.login_history import LoginHistory
from auth_service.src.repository.login_history import LoginHistoryRepository, get_login_history_repository
from auth_service.src.services.base import BaseService


class LoginHistoryService(BaseService[LoginHistory]):
    async def add_login_history(self, user_id: UUID, user_agent: str) -> LoginHistory:
        login_history = LoginHistory(
            user_id=user_id,
            user_agent=user_agent
        )
        return await self.create(login_history)

    async def get_login_history_for_user(self, user_id: UUID) -> List[LoginHistory]:
        return await self.repository.get_login_history_by_user_id(user_id)


@lru_cache()
def get_login_history_service(
        login_history_repository: LoginHistoryRepository = Depends(get_login_history_repository)
) -> LoginHistoryService:
    return LoginHistoryService(login_history_repository)
