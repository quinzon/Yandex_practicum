from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from auth_service.src.core.security import has_permission
from auth_service.src.models.dto.common import BaseResponse, Messages, ErrorMessages
from auth_service.src.models.dto.permission import PermissionCreate, PermissionDto
from auth_service.src.services.permission import PermissionService, get_permission_service

router = APIRouter()


@router.post('/', response_model=PermissionDto)
async def create_permission(
        permission_create: PermissionCreate,
        permission_service: PermissionService = Depends(get_permission_service)
):
    return await permission_service.create(permission_create)


@router.get('/{permission_id}', response_model=PermissionDto)
@has_permission()
async def get_permission(
        request: Request,
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.get_by_id(permission_id)

    if not permission:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.NOT_FOUND)

    return permission


@router.put('/{permission_id}', response_model=PermissionDto)
async def update_permission(
        permission_dto: PermissionDto,
        permission_service: PermissionService = Depends(get_permission_service)
):
    return await permission_service.update(permission_dto)


@router.delete('/{permission_id}')
async def delete_permission(
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    await permission_service.delete(permission_id)
    return BaseResponse(message=Messages.DELETED)
