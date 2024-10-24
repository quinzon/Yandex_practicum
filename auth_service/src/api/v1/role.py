from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Body

from auth_service.src.core.security import has_permission
from auth_service.src.models.dto.common import BaseResponse, Messages, paginated_response, Pagination
from auth_service.src.models.dto.role import RoleCreate, RoleDto, RoleUpdate
from auth_service.src.services.role import RoleService, get_role_service
from auth_service.src.services.role_permission import get_role_permission_service, RolePermissionService

router = APIRouter(dependencies=[Depends(has_permission)])


@router.get('/', response_model=Pagination[RoleDto])
@paginated_response()
async def get_roles(
        role_service: RoleService = Depends(get_role_service),
        page_size: int = Query(10, gt=0, description="Number of items per page"),
        page_number: int = Query(1, gt=0, description="The page number to retrieve"),
):
    return await role_service.get_all(page_size=page_size, page=page_number)


@router.post('/', response_model=RoleDto)
async def create_role(
        role_create: RoleCreate,
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.create(role_create)


@router.get('/{role_id}', response_model=RoleDto)
async def get_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.get_by_id(role_id)


@router.put('/{role_id}', response_model=RoleDto)
async def update_role(
        role_id: UUID,
        role_create: RoleCreate,
        role_service: RoleService = Depends(get_role_service)
):
    role_update = RoleUpdate(id=role_id, **role_create.dict())
    return await role_service.update(role_update)


@router.delete('/{role_id}')
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service)
):
    await role_service.delete(role_id)
    return BaseResponse(message=Messages.DELETED)


@router.put('/{role_id}/permissions', response_model=RoleDto)
async def set_permissions_for_role(
    role_id: UUID,
    permission_ids: List[UUID] = Body(..., embed=True),
    role_permission_service: RolePermissionService = Depends(get_role_permission_service)
):
    return await role_permission_service.set_permissions(role_id, permission_ids)
