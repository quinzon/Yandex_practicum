from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus

from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from auth_service.src.core.security import require_token
from auth_service.src.models.dto.common import ErrorMessages, Messages
from auth_service.src.models.dto.token import TokenResponse, TokenData, RefreshTokenRequest
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.services.user import UserService, get_user_service
from auth_service.src.services.token import TokenService, get_token_service

router = APIRouter()


@router.post('/register', response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = await user_service.register_user(user_data)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=ErrorMessages.USER_ALREADY_EXISTS
        )
    return user


@router.post('/login', response_model=TokenResponse)
async def login_user(
        login_data: LoginRequest,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    user = await user_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.INVALID_CREDENTIALS
        )

    token_data = TokenData(user_id=user.id, email=user.email, roles=user.roles)
    token_response = await token_service.create_tokens(token_data)

    return token_response


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(
        refresh_token_request: RefreshTokenRequest,
        token_service: TokenService = Depends(get_token_service),
        token_data: TokenData = Depends(require_token)
) -> TokenResponse:
    new_tokens = await token_service.refresh_tokens(refresh_token_request.token_value)

    if not new_tokens:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.INVALID_REFRESH_TOKEN
        )

    return new_tokens


@router.post('/logout')
async def logout_user(
    refresh_token_request: RefreshTokenRequest,
    token_service: TokenService = Depends(get_token_service),
    token_data: TokenData = Depends(require_token)
):
    await token_service.revoke_token(refresh_token_request.token_value)

    return JSONResponse(status_code=HTTPStatus.OK, content={"message": Messages.SUCCESSFUL_LOGOUT})
