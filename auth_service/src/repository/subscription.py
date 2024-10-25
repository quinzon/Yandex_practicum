from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.subscription import Subscription
from sqlalchemy import select
from auth_service.src.repository.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def get_model(self) -> Type[Subscription]:
        return Subscription

    async def get_active_subscriptions(self) -> list[Subscription]:
        query = select(Subscription).filter(Subscription.is_active)
        result = await self.session.execute(query)
        return result.scalars().all()


@lru_cache()
def get_subscription_repository(
    session: AsyncSession = Depends(get_session)
) -> SubscriptionRepository:
    return SubscriptionRepository(session)
