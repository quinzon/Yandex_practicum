from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from auth_service.src.core.security import oauth2_scheme
from auth_service.src.models.dto.common import ErrorMessages, BaseResponse, Messages
from auth_service.src.models.dto.role import RoleCreate, RoleDto
from auth_service.src.services.access_control import AccessControlService, \
    get_access_control_service
from auth_service.src.services.role import RoleService, get_role_service

router = APIRouter()


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
        role_dto: RoleDto,
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.update(role_dto)


@router.delete('/{role_id}')
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service)
):
    await role_service.delete(role_id)
    return BaseResponse(message=Messages.DELETED)


@router.post('/check-permission')
async def check_permission(
        resource: str,
        http_method: str,
        access_control_service: AccessControlService = Depends(get_access_control_service),
        token: str = Depends(oauth2_scheme)
):
    has_permission_ = await access_control_service.check_permission(token, resource, http_method)

    if has_permission_:
        return BaseResponse(message=Messages.PERMISSION_GRANTED)
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail=ErrorMessages.PERMISSION_DENIED)
