from uuid import UUID

from fastapi import APIRouter, Depends

from auth_service.src.models.dto.permission import PermissionCreate, PermissionDto, \
    PermissionUpdate
from auth_service.src.services.permission import PermissionService, get_permission_service

router = APIRouter()


@router.post('/permissions', response_model=PermissionDto)
async def create_permission(
        permission_create: PermissionCreate,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.create(permission_create)
    return PermissionDto.from_orm(permission)


@router.get('/permissions/{permission_id}', response_model=PermissionDto)
async def get_permission(
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.get_by_id(permission_id)
    return PermissionDto.from_orm(permission)


@router.put('/permissions/{permission_id}', response_model=PermissionDto)
async def update_permission(
        permission_update: PermissionUpdate,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.update(permission_update)
    return PermissionDto.from_orm(permission)


@router.delete('/permissions/{permission_id}')
async def delete_permission(
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    await permission_service.delete(permission_id)
    return {"message": "Permission deleted"}
