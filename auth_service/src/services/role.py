from functools import lru_cache
from fastapi import HTTPException, Depends
from http import HTTPStatus
from uuid import UUID

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.entities.role import Role
from auth_service.src.models.dto.role import RoleCreate, RoleUpdate
from auth_service.src.repository.role import RoleRepository, get_role_repository
from auth_service.src.services.base import BaseService


class RoleService(BaseService[Role]):
    async def create(self, role_create: RoleCreate) -> Role:
        role = Role(
            name=role_create.name
        )
        return await super().create(role)

    async def update(self, role_update: RoleUpdate) -> Role:
        role = await self.get_by_id(role_update.id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.NOT_FOUND)

        role.name = role_update.name

        return await super().update(role)

    async def delete(self, role_id: UUID) -> None:
        role = await self.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.NOT_FOUND)

        await super().delete(role)


@lru_cache()
def get_role_service(
        role_repository: RoleRepository = Depends(get_role_repository)
) -> RoleService:
    return RoleService(role_repository)
