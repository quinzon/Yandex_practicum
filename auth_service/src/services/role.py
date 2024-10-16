from functools import lru_cache
from typing import List
from http import HTTPStatus

from fastapi import Depends, HTTPException

from auth_service.src.models.dto.role import RoleCreate, RoleResponse
from auth_service.src.repository.role import RoleRepository, get_role_repository
from auth_service.src.models.entities.role import Role
from auth_service.src.services.base import BaseService
from auth_service.src.services.permission import get_permission_service
from auth_service.src.services.client import get_client_service


class RoleService(BaseService[Role]):
    async def create_role(self, role_create: RoleCreate) -> RoleResponse:
        role = Role.create(role_create)
        role = await self.repository.create(role)
        return RoleResponse.from_orm(role)

    async def get_role_permissions(self, role_id: str) -> List[str]:
        role = await self.repository.get_by_id(role_id)
        return [perm.name for perm in role.permissions] if role else []

    async def assign_permission_to_role(self, role_id: str, perm_id: str) -> None:
        await self.repository.assign_permission(role_id, perm_id)

    async def get_role_by_id(self, role_id: str) -> Role | None:
        return await self.repository.get_by_id(role_id)

    async def assign_permissions(self, role_id: str, permissions: List, token: str) -> None:
        permission_service = get_permission_service()
        client = get_client_service(token)
        #role_service = get_role_service()
        if await client.has_permission('edit_role'):
            for permission in permissions:
                permission_name=permission.name
                print(32,permission_name)
                perm_id=await permission_service.get_id_by_name(permission_name)
                if perm_id is None:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Permission '{permission_name}' not found."
                    )
                await self.assign_permission_to_role(role_id, perm_id)    
    
    async def get_id_by_name(self, role_name: str):
        role_id = self.repository.get_id_by_name(role_name)
        if role_id is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role '{role_name}' not found."
            )

@lru_cache()
def get_role_service(
    role_repository: RoleRepository = Depends(get_role_repository)
) -> RoleService:
    return RoleService(role_repository)
