from uuid import UUID
from fastapi import APIRouter, Depends

from auth_service.src.models.dto.role import RoleCreate, RoleDto, RoleUpdate
from auth_service.src.services.role import RoleService, get_role_service

router = APIRouter()


@router.post('/roles', response_model=RoleDto)
async def create_role(
        role_create: RoleCreate,
        role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.create(role_create)
    return RoleDto.from_orm(role)


@router.get('/roles/{role_id}', response_model=RoleDto)
async def get_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.get_by_id(role_id)
    return RoleDto.from_orm(role)


@router.put('/roles/{role_id}', response_model=RoleDto)
async def update_role(
        role_update: RoleUpdate,
        role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.update(role_update)
    return RoleDto.from_orm(role)


@router.delete('/roles/{role_id}')
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service)
):
    await role_service.delete(role_id)
    return {"message": "Role deleted"}
