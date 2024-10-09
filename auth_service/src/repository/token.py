import uuid
from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.token import RefreshToken
from sqlalchemy import select
from auth_service.src.repository.base import BaseRepository


class TokenRepository(BaseRepository[RefreshToken]):
    def get_model(self) -> Type[RefreshToken]:
        return RefreshToken

    async def get_by_user_id(self, user_id: uuid.UUID) -> RefreshToken | None:
        query = select(RefreshToken).filter(RefreshToken.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()


@lru_cache()
def get_token_repository(
    session: AsyncSession = Depends(get_session)
) -> TokenRepository:
    return TokenRepository(session)
