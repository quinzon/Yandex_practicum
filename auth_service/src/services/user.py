from functools import lru_cache
from typing import List

from fastapi import Depends

from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.repository.user import UserRepository, get_user_repository
from auth_service.src.models.entities.user import User
from auth_service.src.services.base import BaseService
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService(BaseService[User]):
    async def register_user(self, user_create: UserCreate) -> UserResponse:
        user = User.create(user_create)
        user = await self.repository.create(user)
        return UserResponse.from_orm(user)

    async def authenticate_user(self, login_data: LoginRequest) -> UserResponse | None:
        user = await self.repository.get_user_by_email(login_data.email)
        if user and self.verify_password(login_data.password, user.password_hash):
            return UserResponse.from_orm(user)
        return None

    async def get_user_roles(self, user_id: str) -> List[str]:
        user = await self.repository.get_by_id(user_id)
        return [role.name for role in user.roles] if user else []

    async def assign_role_to_user(self, user_id: str, role_id: str) -> None:
        await self.repository.assign_role(user_id, role_id)

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.repository.get_by_id(user_id)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


@lru_cache()
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)
