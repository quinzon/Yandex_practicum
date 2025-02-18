from functools import lru_cache
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import HTTPException, Depends

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.models.entities.user import User
from auth_service.src.services.role import RoleService, get_role_service
from auth_service.src.services.user import UserService, get_user_service


class UserRoleService:
    def __init__(self, user_service: UserService, role_service: RoleService):
        self.user_service = user_service
        self.role_service = role_service

    async def set_roles(self, user_id: UUID, role_ids: List[UUID]) -> User:
        user = await self.user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail=ErrorMessages.USER_NOT_FOUND)

        roles = await self.role_service.get_by_ids(role_ids)
        if len(roles) != len(set(role_ids)):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorMessages.NOT_FOUND
            )

        return await self.user_service.set_roles(user, roles)


@lru_cache()
def get_user_role_service(
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service)
) -> UserRoleService:
    return UserRoleService(user_service, role_service)
