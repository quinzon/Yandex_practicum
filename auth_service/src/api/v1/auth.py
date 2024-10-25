from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth_service.src.core.helpers import get_loging_info
from auth_service.src.core.oauth import oauth
from auth_service.src.core.security import oauth2_scheme
from auth_service.src.models.dto.common import ErrorMessages, Messages
from auth_service.src.models.dto.token import TokenResponse, TokenData, RefreshTokenRequest
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.services.login_history import LoginHistoryService, get_login_history_service
from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.services.user import UserService, get_user_service

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
        request: Request,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service),
        login_history_service: LoginHistoryService = Depends(get_login_history_service),
) -> TokenResponse:
    user = await user_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.INVALID_CREDENTIALS
        )

    user_agent, client_address = get_loging_info(request)
    await login_history_service.add_login_history(user.id, user_agent, client_address)

    token_data = TokenData(user_id=user.id, email=user.email, roles=user.roles)
    token_response = await token_service.create_tokens(token_data)

    return token_response


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(
        refresh_token_request: RefreshTokenRequest,
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    token_data, db_token = await token_service.check_refresh_token(
        refresh_token_request.refresh_token)

    user = await user_service.get_by_id(token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.INVALID_CREDENTIALS
        )

    actual_token_data = TokenData(user_id=str(user.id), email=user.email, roles=user.roles)
    new_tokens = await token_service.refresh_tokens(actual_token_data, db_token)

    if not new_tokens:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.INVALID_REFRESH_TOKEN
        )

    return new_tokens


@router.post('/logout')
async def logout_user(
        refresh_token_request: RefreshTokenRequest,
        access_token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_token_service),
):
    await token_service.revoke_token(access_token, refresh_token_request.refresh_token)

    return JSONResponse(status_code=HTTPStatus.OK, content={'message': Messages.SUCCESSFUL_LOGOUT})


@router.get('/external/{provider_name}')
async def login_with_provider(provider_name: str, request: Request):
    client = oauth.create_client(provider_name)
    if not client:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=ErrorMessages.UNSUPPORTED_PROVIDER)

    redirect_uri = request.url_for('auth_callback', provider_name=provider_name)
    return await client.authorize_redirect(request, redirect_uri)


@router.get('/external/{provider_name}/callback')
async def auth_callback(
        provider_name: str,
        request: Request,
        login_history_service: LoginHistoryService = Depends(get_login_history_service),
        user_service: UserService = Depends(get_user_service),
        token_service: TokenService = Depends(get_token_service),
):
    client = oauth.create_client(provider_name)
    if not client:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=ErrorMessages.UNSUPPORTED_PROVIDER)

    token = await client.authorize_access_token(request)

    user_info_response = await client.userinfo(token=token)
    user_info = user_info_response

    user = await user_service.get_or_create_oauth_user(provider_name, user_info)

    user_agent, client_address = get_loging_info(request)
    await login_history_service.add_login_history(user.id, user_agent, client_address)

    token_data = TokenData(user_id=user.id, email=user.email, roles=user.roles)
    token_response = await token_service.create_tokens(token_data)

    return token_response
