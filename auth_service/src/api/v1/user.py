from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from auth_service.src.core.security import oauth2_scheme
from auth_service.src.models.dto.common import ErrorMessages, paginated_response, Pagination, Messages, BaseResponse
from auth_service.src.models.dto.user import UserResponse, UpdateProfileRequest, LoginHistoryResponse
from auth_service.src.services.access_control import AccessControlService, get_access_control_service
from auth_service.src.services.login_history import LoginHistoryService, get_login_history_service
from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.services.user import UserService, get_user_service
from auth_service.src.services.user_role import UserRoleService, get_user_role_service
from auth_service.src.core.security import has_permission

router = APIRouter()


@router.get('/profile', response_model=UserResponse)
async def get_profile(
        user_id: UUID,
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service),
        access_control_service: AccessControlService = Depends(get_access_control_service)
):
    token_data = await token_service.check_access_token(token)

    if not user_id and token_data:
        user_id = UUID(token_data.user_id)

    user = await user_service.get_by_id(user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND)

    if token_data:
        if user_id != token_data.user_id:
            has_permission = await access_control_service.check_permission(token, "user:get_profile", "GET")
            if not has_permission:
                raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=ErrorMessages.PERMISSION_DENIED)
            user.roles = []
            user.email = None
            user.phone_number = None

    return user


@router.put('/profile', response_model=UserResponse)
async def update_profile(
        update_data: UpdateProfileRequest,
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service)
):
    token_data = await token_service.check_access_token(token)
    user = await user_service.get_by_id(UUID(token_data.user_id)) if token_data else None
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND)

    user.first_name = update_data.first_name
    user.last_name = update_data.last_name
    user.patronymic = update_data.patronymic
    user.phone_number = update_data.phone_number
    if update_data.password:
        user.password_hash = user_service.hash_password(update_data.password.get_secret_value())

    return await user_service.update(user)


@router.get('/profile/login-history', response_model=Pagination[LoginHistoryResponse])
@paginated_response()
async def get_login_history(
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        login_history_service: LoginHistoryService = Depends(get_login_history_service),
        page_size: int = Query(10, gt=0, description='Number of items per page'),
        page_number: int = Query(1, gt=0, description='The page number to retrieve'),
):
    token_data = await token_service.check_access_token(token)

    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token data")

    return await login_history_service.get_login_history(
        token_data.user_id,
        page_size,
        page_number
    )


@router.put('/{user_id}/roles', response_model=UserResponse)
async def set_roles_for_user(
    user_id: UUID,
    role_ids: List[UUID] = Body(..., embed=True),
    user_role_service: UserRoleService = Depends(get_user_role_service),
    _: None = Depends(has_permission)
):
    return await user_role_service.set_roles(user_id, role_ids)


@router.get('/check-permission')
async def check_permission(
        resource: str,
        http_method: str,
        access_control_service: AccessControlService = Depends(get_access_control_service),
        token: str = Depends(oauth2_scheme)
):
    has_permission_ = await access_control_service.check_permission(token, resource, http_method)

    if has_permission_:
        return BaseResponse(message=Messages.PERMISSION_GRANTED)

    raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                        detail=ErrorMessages.PERMISSION_DENIED)


@router.get('/users', response_model=Pagination[UserResponse])
@paginated_response()
async def get_users(
        role_id: UUID,
        page_size: int = Query(10, gt=0, description='Number of items per page'),
        page_number: int = Query(1, gt=0, description='The page number to retrieve'),
        token: str = Depends(oauth2_scheme),
        user_service: UserService = Depends(get_user_service),
        access_control_service: AccessControlService = Depends(get_access_control_service)
):
    has_permission = await access_control_service.check_permission(token, "user:get_users", "GET")
    if not has_permission:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=ErrorMessages.PERMISSION_DENIED)

    return await user_service.get_all_users(role_id=str(role_id), page_size=page_size, page_number=page_number)
