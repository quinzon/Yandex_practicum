import hashlib
from http import HTTPStatus

import bcrypt
import uuid
from datetime import timedelta, datetime
from functools import lru_cache

from fastapi import HTTPException, Depends
from jose import JWTError, jwt

from auth_service.src.core.config import JWTSettings, get_jwt_settings
from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.dto.token import TokenData, TokenResponse
from auth_service.src.models.entities.token import RefreshToken
from auth_service.src.repository.token import TokenRepository, get_token_repository


class TokenService:
    def __init__(self, settings: JWTSettings, token_repository: TokenRepository):
        self.settings = settings
        self.token_repository = token_repository

    def _hash_token(self, token: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(token.encode('utf-8'))
        return sha256.hexdigest()

    def create_access_token(self, token_data: TokenData) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)

        to_encode = {
            'sub': token_data.user_id,
            'email': token_data.email,
            'roles': token_data.roles,
            'exp': expire
        }

        token = jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)
        return token

    async def create_refresh_token(self, token_data: TokenData) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.refresh_token_expire_minutes)

        to_encode = {
            'sub': token_data.user_id,
            'exp': expire,
            'email': token_data.email,
        }

        refresh_token = jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)

        hashed_token = self._hash_token(refresh_token)

        existing_token = await self.token_repository.get_by_user_id(uuid.UUID(token_data.user_id))

        if existing_token:
            existing_token.token_value = hashed_token
            existing_token.expires_at = expire
            existing_token.created_at = datetime.utcnow()
            await self.token_repository.update(existing_token)
        else:
            token_entry = RefreshToken(
                user_id=uuid.UUID(token_data.user_id),
                token_value=hashed_token,
                expires_at=expire,
                created_at=datetime.utcnow()
            )
            await self.token_repository.create(token_entry)

        return refresh_token

    async def create_tokens(self, token_data: TokenData) -> TokenResponse:
        access_token = self.create_access_token(token_data)
        refresh_token = await self.create_refresh_token(token_data)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def verify_token(self, token: str) -> TokenData | None:
        try:
            payload = jwt.decode(token, self.settings.secret_key, algorithms=[self.settings.algorithm])
            user_id: str = payload.get('sub')
            email: str = payload.get('email')
            roles: list = payload.get('roles', [])

            if user_id is None or email is None:
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_ACCESS_TOKEN)

            return TokenData(user_id=user_id, email=email, roles=roles)
        except JWTError as e:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ErrorMessages.INVALID_ACCESS_TOKEN
            )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_data = await self.verify_token(refresh_token)

        if not token_data:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_REFRESH_TOKEN)

        db_token = await self.token_repository.get_by_user_id(uuid.UUID(token_data.user_id))

        if not db_token or self._hash_token(refresh_token) != db_token.token_value:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_REFRESH_TOKEN)

        await self.token_repository.delete(db_token)

        return await self.create_tokens(token_data)

    async def revoke_token(self, refresh_token: str) -> None:
        token_data = await self.verify_token(refresh_token)
        if not token_data:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_REFRESH_TOKEN)

        db_token = await self.token_repository.get_by_user_id(uuid.UUID(token_data.user_id))
        if not db_token:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_REFRESH_TOKEN)

        if self._hash_token(refresh_token) != db_token.token_value:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=ErrorMessages.INVALID_REFRESH_TOKEN)

        await self.token_repository.delete(db_token)


@lru_cache()
def get_token_service(
    jwt_settings: JWTSettings = Depends(get_jwt_settings),
    token_repository: TokenRepository = Depends(get_token_repository)
) -> TokenService:
    return TokenService(jwt_settings, token_repository)
