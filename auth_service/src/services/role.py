from functools import lru_cache
from typing import List, Optional
from http import HTTPStatus

from fastapi import Depends, HTTPException

from auth_service.src.models.dto.role import RoleCreate, RoleResponse
from auth_service.src.repository.role import RoleRepository, get_role_repository
from auth_service.src.models.entities.role import Role
from auth_service.src.services.base import BaseService
from auth_service.src.services.permission import get_permission_service
from auth_service.src.services.client import get_client,Client
from auth_service.src.repository.base import BaseRepository
from auth_service.src.repository.permission import PermissionRepository,get_permission_repository


class RoleService(BaseService[Role]):
    def __init__(self, repository: BaseRepository[Role],
                 client: Client,
                 permission_repository: PermissionRepository,
                 ):
        super().__init__(repository)
        self.client = client
        self.permission_repository = permission_repository
    
    async def create_role(self, role_create: RoleCreate) -> RoleResponse:
        role = Role.create(role_create)
        role = await self.repository.create(role)
        return RoleResponse.from_orm(role)

    async def get_role_permissions(self, role_id: str) -> List[str]:
        role = await self.get_role_by_id(role_id)
        return [perm.name for perm in role.permissions] if role else []

    async def assign_permission_to_role(self, role_id: str, perm_id: str) -> None:
        await self.repository.assign_permission(role_id, perm_id)

    async def get_role_by_id(self, role_id: str) -> Role | None:
        return await self.repository.get_by_id(role_id)

    async def assign_permissions(self, role_id: str, permission_names: List[str], token: str) -> Role | None:
        self.client.set_token(token)
        if await self.client.has_permission('edit_role'):
            for permission_name in permission_names:
                perm_id=await self.permission_repository.get_id_by_name(permission_name)
                if perm_id is None:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Permission '{permission_name}' not found."
                    )
                await self.assign_permission_to_role(role_id, perm_id)    
        return await self.get_role_by_id(role_id)
    
    async def get_id_by_name(self, role_name: str):
        role_id = self.repository.get_id_by_name(role_name)
        if role_id is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Role '{role_name}' not found."
            )
    async def revoke_permissions(self, role_id: str, permission_names: List[str], token: str) -> Role | None:
        self.client.set_token(token)      
        if await self.client.has_permission('edit_role'):
            for permission_name in permission_names:
                perm_id = await self.permission_repository.get_id_by_name(permission_name)
                if perm_id is None:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Permission '{permission_name}' not found."
                    )
                await self.remove_permission_from_role(role_id, perm_id)
        return await self.get_role_by_id(role_id)
    
    async def remove_permission_from_role(self, role_id: str, perm_id: str) -> None:
        await self.repository.remove_permission(role_id, perm_id)


@lru_cache()
def get_role_service(
    role_repository: RoleRepository = Depends(get_role_repository),
    client: Client = Depends(get_client),
    permission_repository: PermissionRepository = Depends(get_permission_repository)
) -> RoleService:
    return RoleService(role_repository,
                       client,
                       permission_repository)