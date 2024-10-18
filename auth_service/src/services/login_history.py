from functools import lru_cache
from typing import List, Tuple

from fastapi import Depends

from auth_service.src.models.entities.login_history import LoginHistory
from auth_service.src.repository.login_history import (LoginHistoryRepository,
                                                       get_login_history_repository)
from auth_service.src.services.base import BaseService


class LoginHistoryService(BaseService[LoginHistory]):
    async def add_login_history(self, user_id: str, user_agent: str,
                                client_address: str) -> LoginHistory:
        login_history = LoginHistory(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=client_address
        )
        return await self.create(login_history)

    async def get_login_history(
        self,
        user_id: str,
        page_size: int = 10,
        page_number: int = 1
    ) -> Tuple[List[LoginHistory], int]:
        return await self.repository.get_login_history(user_id, page_size, page_number)


@lru_cache()
def get_login_history_service(
        login_history_repository: LoginHistoryRepository = Depends(get_login_history_repository)
) -> LoginHistoryService:
    return LoginHistoryService(login_history_repository)
