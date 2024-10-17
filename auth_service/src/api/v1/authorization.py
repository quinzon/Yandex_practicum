from uuid import uuid4, UUID
from typing import List, Optional
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

from auth_service.src.models.dto.common import ErrorMessages, Messages
from auth_service.src.models.dto.token import TokenBearer
from auth_service.src.models.dto.role import RoleCreate, RoleResponse, Role
from auth_service.src.models.dto.permission import Permission
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.services.role import RoleService, get_role_service
from auth_service.src.services.user import UserService, get_user_service
from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.api.v1.auth import login_user 

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/token", response_model=TokenBearer,
    summary='Used by Swagger "Authorize" function')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service)
    ):
    '''Для авторизации в Swagger'''
    login_data= LoginRequest(email = form_data.username,
                            password = form_data.password)
    token_response = await login_user(login_data, user_service, token_service)
    return TokenBearer(access_token=token_response.access_token)

@router.post("/roles/create")
async def create_role(role_data: RoleCreate,
 role_service: RoleService = Depends(get_role_service),
):
    '''Создание роли'''
    try:
        role = await role_service.create_role(role_data)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=ErrorMessages.ROLE_ALREADY_EXISTS
        )
    return role

@router.get("/roles/{role_id}", response_model=RoleResponse,
    summary='Get Role Permissions')
async def get_role(role_id: UUID,
 role_service: RoleService = Depends(get_role_service)
):
    '''Получить разрешения роли'''
    try:
        role = await role_service.get_role_by_id(role_id)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def assign_permissions_to_role(role_id: UUID,
 permissions: List[Permission],
 role_service: RoleService = Depends(get_role_service),
 token: str = Depends(oauth2_scheme)
):
    '''Назначение разрешений роли'''
    if not permissions: 
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No permissions set'
        )
    #try:
    role = await role_service.assign_permissions(role_id, permissions, token)
    '''except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )'''
    return role

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID,
 user_service: UserService = Depends(get_user_service)
):
    '''Просмотр пользователя'''
    try:
        user = await user_service.get_user_by_id(user_id)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.USER_NOT_FOUND
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def assign_role_to_user(user_id: UUID,
 roles: List[Role],
 user_service: UserService = Depends(get_user_service),
):
    '''Назначение роли пользователю'''
    if not roles: 
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No roles set'
        )
    try:
        user = await user_service.assign_roles(user_id, roles)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
    return user