from typing import List
from uuid import UUID
from http import HTTPStatus
from passlib.context import CryptContext
import logging

from fastapi import Depends, HTTPException

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.models.entities.role import Role
from auth_service.src.models.entities.user import User
from auth_service.src.repository.user import UserRepository, get_user_repository
from auth_service.src.services.base import BaseService
from auth_service.src.core.helpers import generate_password
from auth_service.src.services.token import TokenService, get_token_service

logger = logging.getLogger('UserService')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService(BaseService[User]):
    def __init__(self, repository: UserRepository, token_service: TokenService):
        super().__init__(repository)
        self.repository: UserRepository = repository
        self.token_service: TokenService = token_service

    async def register_user(self, user_create: UserCreate) -> UserResponse:
        user = User.create(user_create)
        user = await self.create(user)
        return UserResponse.from_orm(user)

    async def authenticate_user(self, login_data: LoginRequest) -> UserResponse | None:
        user = await self.repository.get_user_by_email(login_data.email)
        if user and self.verify_password(login_data.password, user.password_hash):
            return UserResponse.from_orm(user)
        return None

    async def get_user_roles(self, user_id: str) -> List[str]:
        user = await self.get_by_id(UUID(user_id))
        return [role.name for role in user.roles] if user else []

    async def assign_role_to_user(self, user_id: str, role_id: str) -> None:
        await self.repository.assign_role(user_id, role_id)

    async def set_roles(self, user: User, roles: List[Role]) -> User:
        user.roles = roles
        await self.update(user)
        return user

    async def get_or_create_oauth_user(self, provider_name: str, user_info: dict) -> User:
        provider_user_id = self._get_provider_user_id(user_info)

        social_account = await self.repository.get_social_account(provider_name, provider_user_id)
        if social_account:
            return social_account.user

        email = self._get_user_email(user_info)
        user = await self.repository.get_user_by_email(email)

        if not user:
            logger.info(f'Creating new user from {provider_name} with email {email}')
            password = self.hash_password(generate_password())
            user = await self.repository.create_user(
                email=email,
                first_name=user_info.get('first_name', ''),
                last_name=user_info.get('last_name', ''),
                patronymic=user_info.get('patronymic', ''),
                phone_number=user_info.get('phone_number', ''),
                password_hash=self.hash_password(password),
            )

        await self.repository.create_social_account(
            user=user,
            provider=provider_name,
            provider_user_id=provider_user_id,
            extra_data=user_info,
        )

        return user

    async def get_users(self, role_name: str | None, page_size: int = 10, page_number: int = 1) -> tuple[list, int]:
        users = await self.repository.get_users_by_role(role_name, page_size, page_number)
        total_count = await self.repository.get_total_users_count(role_name)
        user_responses = [UserResponse.from_orm(user) for user in users]
        return user_responses, total_count

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_user_by_email(email)

    async def get_user_by_token(self, token: str) -> User | None:
        token_data = await self.token_service.check_access_token(token)
        if not token_data.user_id:
            return None
        return await self.get_by_id(UUID(token_data.user_id))

    def _get_provider_user_id(self, user_info: dict) -> str:
        provider_user_id = user_info.get('id')
        if not provider_user_id:
            logger.error('Missing "id" from OAuth provider user_info')
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessages.MISSING_PROVIDER_ID,
            )
        return provider_user_id

    def _get_user_email(self, user_info: dict) -> str:
        email = user_info.get('email') or user_info.get('default_email')
        if not email:
            logger.error('No email provided in user_info')
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessages.NO_EMAIL_PROVIDED,
            )

        if isinstance(email, list):
            email = email[0]

        return email

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
        token_service: TokenService = Depends(get_token_service)
) -> UserService:
    return UserService(user_repository, token_service)
