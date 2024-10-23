from functools import lru_cache
from http import HTTPStatus
from fastapi import HTTPException, Depends
from typing import List
from uuid import UUID

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.entities.role import Role
from auth_service.src.services.permission import PermissionService, get_permission_service
from auth_service.src.services.role import RoleService, get_role_service


class RolePermissionService:
    def __init__(self, role_service: RoleService, permission_service: PermissionService):
        self.role_service = role_service
        self.permission_service = permission_service

    async def set_permissions(self, role_id: UUID, permission_ids: List[UUID]) -> Role:
        role = await self.role_service.get_by_id(role_id)

        permissions = await self.permission_service.get_by_ids(permission_ids)

        if len(permissions) != len(set(permission_ids)):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessages.NOT_FOUND
            )

        updated_role = await self.role_service.set_permissions(role, permissions)
        return updated_role


@lru_cache()
def get_role_permission_service(
    role_service: RoleService = Depends(get_role_service),
    permission_service: PermissionService = Depends(get_permission_service),
) -> RolePermissionService:
    return RolePermissionService(role_service, permission_service)
