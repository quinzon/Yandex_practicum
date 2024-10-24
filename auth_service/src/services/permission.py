from functools import lru_cache
from typing import List
from http import HTTPStatus
from uuid import UUID

from sqlalchemy import select
from fastapi import HTTPException, Depends

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.entities.permission import Permission
from auth_service.src.models.dto.permission import PermissionCreate, PermissionDto
from auth_service.src.repository.permission import PermissionRepository, get_permission_repository
from auth_service.src.services.base import BaseService


class PermissionService(BaseService[Permission]):
    async def create(self, permission_create: PermissionCreate) -> Permission:
        permission = Permission(
            name=permission_create.name,
            http_method=permission_create.http_method,
            resource=permission_create.resource
        )
        return await super().create(permission)

    async def update(self, permission_dto: PermissionDto) -> Permission:
        permission = await self.get_by_id(permission_dto.id)

        permission.name = permission_dto.name
        permission.http_method = permission_dto.http_method
        permission.resource = permission_dto.resource

        return await super().update(permission)

    async def delete(self, permission_id: UUID) -> None:
        permission = await self.get_by_id(permission_id)
        if not permission:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.NOT_FOUND)

        await super().delete(permission)

    async def get_by_ids(self, permission_ids: List[UUID]) -> List[Permission]:
        result = await self.repository.session.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )
        return result.scalars().all()


@lru_cache()
def get_permission_service(
        permission_repository: PermissionRepository = Depends(get_permission_repository)
) -> PermissionService:
    return PermissionService(permission_repository)
