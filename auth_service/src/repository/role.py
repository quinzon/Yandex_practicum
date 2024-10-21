from functools import lru_cache
from typing import Type

from fastapi import Depends
from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from auth_service.src.db.postgres import get_session
from auth_service.src.models.entities.role import Role, role_permission
from auth_service.src.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def get_model(self) -> Type[Role]:
        return Role

    async def assign_permission(self, role_id: str, perm_id: str) -> None:
        try:
            query = insert(role_permission).values(role_id=role_id, permission_id=perm_id)
            await self.session.execute(query)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

    async def remove_permission(self, role_id: str, perm_id: str) -> None:
        try:
            query = delete(role_permission).where(
                role_permission.c.role_id == role_id,
                role_permission.c.permission_id == perm_id
            )
            await self.session.execute(query)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

    async def delete_role(self, role_id: str) -> None:
        try:
            query = delete(Role).where(Role.id == role_id)
            await self.session.execute(query)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()


@lru_cache()
def get_role_repository(
    session: AsyncSession = Depends(get_session)
) -> RoleRepository:
    return RoleRepository(session)
