import hashlib
import uuid
from datetime import timedelta, datetime
from functools import lru_cache
from http import HTTPStatus

from typing import Tuple

from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from redis.asyncio import Redis

from auth_service.src.core.config import JWTSettings, get_jwt_settings
from auth_service.src.db.redis import get_redis
from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.dto.token import TokenData, TokenResponse
from auth_service.src.models.entities.token import RefreshToken
from auth_service.src.repository.token import TokenRepository, get_token_repository


class TokenService:
    def __init__(self, settings: JWTSettings, token_repository: TokenRepository, redis: Redis):
        self.settings = settings
        self.token_repository = token_repository
        self.redis = redis

    @staticmethod
    def _hash_token(token: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(token.encode('utf-8'))
        return sha256.hexdigest()

    @staticmethod
    def _get_ttl(payload: dict) -> float:
        exp: float = float(str(payload.get('exp')))
        expire_datetime = datetime.utcfromtimestamp(exp)
        now = datetime.utcnow()
        return (expire_datetime - now).total_seconds()

    def create_access_token(self, token_data: TokenData) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)

        is_superuser = 'superadmin' in token_data.roles if token_data.roles else False

        to_encode = {
            'sub': token_data.user_id,
            'email': token_data.email,
            'roles': token_data.roles,
            'exp': expire,
            'is_superuser': is_superuser
        }

        return jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)

    async def create_refresh_token(self, token_data: TokenData) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.settings.refresh_token_expire_minutes)

        to_encode = {
            'sub': token_data.user_id,
            'exp': expire,
            'email': token_data.email,
            'jti': str(uuid.uuid4()),
        }

        refresh_token = jwt.encode(to_encode, self.settings.secret_key,
                                   algorithm=self.settings.algorithm)

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

    async def is_token_blacklisted(self, access_token: str) -> bool:
        blacklist_key = f'blacklist:{access_token}'
        return await self.redis.exists(blacklist_key)

    async def check_access_token(self, access_token: str) -> TokenData | None:
        token_data = await self.get_token_data(access_token)
        if await self.is_token_blacklisted(access_token):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail=ErrorMessages.TOKEN_REVOKED)
        return token_data

    async def check_refresh_token(self, refresh_token: str) -> Tuple[TokenData | None, RefreshToken]:
        token_data = await self.get_token_data(refresh_token)
        db_token = await self.token_repository.get_by_user_id(uuid.UUID(token_data.user_id)) if token_data else None
        if not db_token or self._hash_token(refresh_token) != db_token.token_value:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail=ErrorMessages.INVALID_REFRESH_TOKEN)
        return token_data, db_token

    async def get_token_data(self, token: str) -> TokenData | None:
        payload = self._verify_token(token)
        if payload:
            user_id: str | None = payload.get('sub')
            email: str | None = payload.get('email')
            roles: list = payload.get('roles', [])
            is_superuser: bool = payload.get('is_superuser', False)
        else:
            user_id = ""
            email = ""
            roles = []
            is_superuser = False
        if not is_superuser:
            is_superuser = False
        return TokenData(user_id=user_id, email=email, roles=roles, is_superuser=is_superuser)

    def _verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.settings.secret_key,
                                 algorithms=[self.settings.algorithm])
        except JWTError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail=ErrorMessages.INVALID_TOKEN)
        if self._get_ttl(payload) <= 0:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail=ErrorMessages.TOKEN_EXPIRED)
        return payload

    async def refresh_tokens(self, token_data: TokenData, db_token: RefreshToken) -> TokenResponse:
        await self.token_repository.delete(db_token)
        return await self.create_tokens(token_data)

    async def revoke_token(self, access_token: str, refresh_token: str) -> None:
        refresh_token_data, db_token = await self.check_refresh_token(refresh_token)
        await self.token_repository.delete(db_token)
        await self.add_blacklist(access_token)

    async def add_blacklist(self, access_token: str) -> None:
        payload = self._verify_token(access_token)
        if not payload:
            raise ValueError("Invalid token: payload is None")
        blacklist_key = f'blacklist:{access_token}'
        ttl = self._get_ttl(payload)
        await self.redis.set(blacklist_key, 'true', ex=int(ttl if ttl > 0 else 0))


@lru_cache()
def get_token_service(
        jwt_settings: JWTSettings = Depends(get_jwt_settings),
        token_repository: TokenRepository = Depends(get_token_repository),
        redis: Redis = Depends(get_redis)
) -> TokenService:
    return TokenService(jwt_settings, token_repository, redis)
