from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.token import RefreshToken
from sqlalchemy import select
from auth_service.src.repository.base import BaseRepository


class TokenRepository(BaseRepository[RefreshToken]):
    async def get_token_by_value(self, token_value: str) -> RefreshToken:
        query = select(RefreshToken).filter(RefreshToken.token_value == token_value)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def revoke_token(self, token_value: str) -> None:
        token = await self.get_token_by_value(token_value)
        if token:
            await self.delete(token)


@lru_cache()
def get_subscription_repository(
    session: AsyncSession = Depends(get_session)
) -> TokenRepository:
    return TokenRepository(session)
