from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.role import Role
from auth_service.src.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def get_model(self) -> Type[Role]:
        return Role


@lru_cache()
def get_role_repository(
    session: AsyncSession = Depends(get_session)
) -> RoleRepository:
    return RoleRepository(session)
