from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from uuid import uuid4, UUID
from typing import List, Optional
from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.services.role import RoleService, get_role_service

from auth_service.src.core.security import require_token
from auth_service.src.models.dto.common import ErrorMessages, Messages
from auth_service.src.models.dto.token import TokenResponse, TokenData, RefreshTokenRequest
from auth_service.src.models.dto.role import RoleCreate, RoleResponse
from auth_service.src.models.dto.permission import Permission
from auth_service.src.services.token import TokenService, get_token_service

router = APIRouter()

# Создание роли
@router.post("/roles/create")
async def create_role(role_data: RoleCreate,
 role_service: RoleService = Depends(get_role_service),
):
    try:
        role = await role_service.create_role(role_data)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=ErrorMessages.ROLE_ALREADY_EXISTS
        )
    return role

# разрешения роли
@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID,
 role_service: RoleService = Depends(get_role_service),
):
    try:
        role = await role_service.get_role_by_id(role_id)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
    return role

# назначение разрешений роли
@router.put("/roles/{role_id}", response_model=RoleResponse)
async def assign_permissions_to_role(role_id: UUID,
 permissions: List[Permission],
 role_service: RoleService = Depends(get_role_service),
):
    if not permissions: 
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No permissions set'
        )
    try:
        role = await role_service.assign_permissions(role_id, permissions)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
    return role
