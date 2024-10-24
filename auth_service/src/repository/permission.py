from functools import lru_cache
from typing import Type, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.permission import Permission
from auth_service.src.repository.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def get_model(self) -> Type[Permission]:
        return Permission

    async def get_by_ids(self, permission_ids: List[UUID]) -> List[Permission]:
        result = await self.session.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        return result.scalars().all()


@lru_cache()
def get_permission_repository(
    session: AsyncSession = Depends(get_session)
) -> PermissionRepository:
    return PermissionRepository(session)
