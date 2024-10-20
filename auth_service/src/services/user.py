from functools import lru_cache
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

from auth_service.src.models.dto.user import UserCreate, UserResponse, LoginRequest
from auth_service.src.repository.user import UserRepository, get_user_repository
from auth_service.src.repository.role import RoleRepository, get_role_repository
from auth_service.src.models.entities.user import User
from auth_service.src.models.entities.role import Role
from auth_service.src.services.base import BaseService
from auth_service.src.repository.base import BaseRepository
from auth_service.src.services.client import get_client,Client
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserService(BaseService[User]):
    def __init__(self, repository: BaseRepository[User],
                 client: Client,
                 role_repository: BaseRepository[Role],
                 ):
        super().__init__(repository)
        self.client = client
        self.role_repository = role_repository

    async def register_user(self, user_create: UserCreate) -> UserResponse:
        user = User.create(user_create)
        user = await self.repository.create(user)
        return UserResponse.from_orm(user)

    async def authenticate_user(self, login_data: LoginRequest) -> UserResponse | None:
        user = await self.repository.get_user_by_email(login_data.email)
        if user and self.verify_password(login_data.password, user.password_hash):
            # return UserResponse.from_orm(user) # UserResponse хочет string, а ему дают object
            roles = [role.name for role in user.roles]
            return UserResponse(id=user.id,
                                  email=user.email, 
                                  first_name=user.first_name, 
                                  last_name=user.last_name, 
                                  roles=roles)
        return None

    async def get_user_roles(self, user_id: str) -> List[str]:
        user = await self.repository.get_by_id(user_id)
        return [role.name for role in user.roles] if user else []

    async def assign_role_to_user(self, user_id: str, role_id: str) -> None:
        await self.repository.assign_role(user_id, role_id)

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def assign_roles(self, user_id: str, role_names: List[str], token: str) -> User | None:
        self.client.set_token(token)
        if await self.client.has_permission('edit_user'):
            for role_name in role_names:
                role_id=await self.role_repository.get_id_by_name(role_name)
                await self.assign_role_to_user(user_id, role_id)
        return await self.get_user_by_id(user_id)

    async def revoke_roles(self, user_id: str, role_names: List[str], token: str) -> None:
        self.client.set_token(token)
        if await self.client.has_permission('edit_user'):
            for role_name in role_names:
                role_id = await self.role_repository.get_id_by_name(role_name)
                await self.repository.remove_role_from_user(user_id, role_id)
        return await self.get_user_by_id(user_id)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


@lru_cache()
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    client: Client = Depends(get_client),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> UserService:
    return UserService(user_repository, client, role_repository)
