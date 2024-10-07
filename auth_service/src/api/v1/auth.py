from fastapi import APIRouter, Depends, HTTPException, status
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.services.user import UserService
from auth_service.src.services.token_service import TokenService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(
        user_data: UserCreate,
        user_service: UserService = Depends(),
):
    user = await user_service.register_user(user_data)
    return user


@router.post("/login")
async def login_user(
        login_data: LoginRequest,
        user_service: UserService = Depends(),
        token_service: TokenService = Depends()
):
    user = await user_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token, refresh_token = token_service.create_tokens(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh")
async def refresh_token(
        refresh_token: str,
        token_service: TokenService = Depends()
):
    new_tokens = await token_service.refresh_tokens(refresh_token)

    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    return new_tokens
