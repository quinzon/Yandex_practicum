from uuid import UUID
from http import HTTPStatus

from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.dto.token import TokenBearer
from auth_service.src.models.dto.role import RoleCreate, RoleNestedResponse
from auth_service.src.models.dto.user import UserResponse, LoginRequest, UserNestedResponse
from auth_service.src.models.dto.permission import PermissionUpdateRequest
from auth_service.src.models.dto.role import RoleUpdateRequest
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
    login_data = LoginRequest(email=form_data.username,
                              password=form_data.password)
    token_response = await login_user(login_data, request=None, user_service=user_service, token_service=token_service)
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


@router.get("/roles/{role_id}", response_model=RoleNestedResponse,
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
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
    return role


@router.patch("/roles/{role_id}/permissions", response_model=RoleNestedResponse)
async def update_permissions_for_role(role_id: UUID,
                                      permissions: PermissionUpdateRequest,
                                      role_service: RoleService = Depends(
                                          get_role_service),
                                      token: str = Depends(oauth2_scheme)):
    '''Добавление и удаление разрешений роли'''

    if not permissions.add and not permissions.remove:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No permissions set'
        )

    try:
        if permissions.add:
            await role_service.assign_permissions(role_id, permissions.add, token)

        if permissions.remove:
            await role_service.revoke_permissions(role_id, permissions.remove, token)

        # Возвращаем обновленную роль
        return await role_service.get_role_by_id(role_id)

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )


@router.get("/users/{user_id}", response_model=UserNestedResponse)
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


@router.patch("/users/{user_id}/roles", response_model=UserResponse)
async def update_roles_for_user(
        user_id: UUID,
        role_update: RoleUpdateRequest,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme)
):
    '''Добавление и удаление ролей для пользователя'''

    if not role_update.add and not role_update.remove:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No roles set'
        )

    try:
        if role_update.add:
            await user_service.assign_roles(user_id, role_update.add, token)

        if role_update.remove:
            await user_service.revoke_roles(user_id, role_update.remove, token)

        updated_user = await user_service.get_user(user_id)
        return updated_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.USER_NOT_FOUND
        )


@router.delete("/roles/{role_id}", response_model=dict)
async def delete_role(role_id: UUID,
                      role_service: RoleService = Depends(get_role_service),
                      token: str = Depends(oauth2_scheme)
                      ):
    '''Удаление роли'''
    try:
        await role_service.delete_role(role_id, token)
        return {"detail": f"Role with ID {role_id} has been deleted."}
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.ROLE_NOT_FOUND
        )
