from typing import List
from fastapi import Depends, HTTPException
from http import HTTPStatus
from passlib.context import CryptContext
import logging

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.models.entities.role import Role
from auth_service.src.models.entities.user import User
from auth_service.src.repository.user import UserRepository, get_user_repository
from auth_service.src.services.base import BaseService
from auth_service.src.core.helpers import generate_password

from sqlalchemy.future import select
from sqlalchemy.sql import func


logger = logging.getLogger('UserService')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService(BaseService[User]):
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
        user = await self.get_by_id(user_id)
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

    async def get_all_users(self, role_id: str = None, page_size: int = 10, page_number: int = 1):
        query = select(User)

        if role_id:
            query = query.join(User.roles).filter(Role.id == role_id)

        total_count = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total_count = total_count.scalar_one()

        result = await self.session.execute(query.offset((page_number - 1) * page_size).limit(page_size))
        users = result.scalars().all()

        return [UserResponse.from_orm(user) for user in users], total_count


def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)
