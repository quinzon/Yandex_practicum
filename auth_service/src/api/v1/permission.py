from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from auth_service.src.core.security import has_permission
from auth_service.src.models.dto.common import BaseResponse, Messages, ErrorMessages, paginated_response, Pagination
from auth_service.src.models.dto.permission import PermissionCreate, PermissionDto, PermissionUpdate
from auth_service.src.services.permission import PermissionService, get_permission_service

router = APIRouter(dependencies=[Depends(has_permission)])


@router.get('/', response_model=Pagination[PermissionDto])
@paginated_response()
async def get_roles(
        permission_service: PermissionService = Depends(get_permission_service),
        page_size: int = Query(10, gt=0, description='Number of items per page'),
        page_number: int = Query(1, gt=0, description='The page number to retrieve'),
):
    return await permission_service.get_all(page_size=page_size, page=page_number)


@router.post('/', response_model=PermissionDto)
async def create_permission(
        permission_create: PermissionCreate,
        permission_service: PermissionService = Depends(get_permission_service)
):
    return await permission_service.create(permission_create)


@router.get('/{permission_id}', response_model=PermissionDto)
async def get_permission(
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.get_by_id(permission_id)

    if not permission:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.NOT_FOUND)

    return permission


@router.put('/{permission_id}', response_model=PermissionDto)
async def update_permission(
        permission_id: UUID,
        permission_dto: PermissionCreate,
        permission_service: PermissionService = Depends(get_permission_service)
):
    permission_update = PermissionUpdate(id=permission_id, **permission_dto.dict())
    return await permission_service.update(permission_update)


@router.delete('/{permission_id}')
async def delete_permission(
        permission_id: UUID,
        permission_service: PermissionService = Depends(get_permission_service)
):
    await permission_service.delete(permission_id)
    return BaseResponse(message=Messages.DELETED)
