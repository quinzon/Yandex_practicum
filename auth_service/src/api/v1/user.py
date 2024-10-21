from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from auth_service.src.core.security import oauth2_scheme
from auth_service.src.models.dto.common import ErrorMessages, paginated_response, Pagination
from auth_service.src.models.dto.user import UserResponse, UpdateProfileRequest, \
    LoginHistoryResponse
from auth_service.src.services.login_history import LoginHistoryService, get_login_history_service
from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.services.user import UserService, get_user_service

router = APIRouter()


@router.get('/profile', response_model=UserResponse)
async def get_profile(
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service)
):
    token_data = await token_service.check_access_token(token)
    user = await user_service.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND)
    return UserResponse.from_orm(user)


@router.put('/profile', response_model=UserResponse)
async def update_profile(
        update_data: UpdateProfileRequest,
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        user_service: UserService = Depends(get_user_service)
):
    token_data = await token_service.check_access_token(token)
    user = await user_service.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessages.USER_NOT_FOUND)

    user.first_name = update_data.first_name
    user.last_name = update_data.last_name
    if update_data.password:
        user.password_hash = user_service.hash_password(update_data.password.get_secret_value())

    updated_user = await user_service.update(user)
    return UserResponse.from_orm(updated_user)


@router.get('/profile/login-history', response_model=Pagination[LoginHistoryResponse])
@paginated_response()
async def get_login_history(
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
        login_history_service: LoginHistoryService = Depends(get_login_history_service),
        page_size: int = Query(10, gt=0, description="Number of items per page"),
        page_number: int = Query(1, gt=0, description="The page number to retrieve"),
):
    token_data = await token_service.check_access_token(token)
    items, total_items = await login_history_service.get_login_history(
        token_data.user_id,
        page_size,
        page_number
    )
    return items, total_items
