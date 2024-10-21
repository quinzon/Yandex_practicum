from functools import lru_cache
from fastapi import Depends

from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.models.entities.role import Role
from auth_service.src.repository.role import RoleRepository, get_role_repository


class AccessControlService:
    def __init__(self, role_repository: RoleRepository, token_service: TokenService):
        self.role_repository = role_repository
        self.token_service = token_service

    async def check_permission(self, token: str, resource: str, http_method: str) -> bool:
        token_data = await self.token_service.check_access_token(token)

        if token_data.get('is_superuser'):
            return True

        roles = token_data.roles

        for role_name in roles:
            role = await self.role_repository.get_by_name(role_name)
            if role and await self._has_permission(role, resource, http_method):
                return True

        return False

    async def _has_permission(self, role: Role, resource: str, http_method: str) -> bool:
        for permission in role.permissions:
            if permission.resource == resource and permission.http_method == http_method:
                return True
        return False


@lru_cache()
def get_access_control_service(
        role_repository: RoleRepository = Depends(get_role_repository),
        token_service: TokenService = Depends(get_token_service)
) -> AccessControlService:
    return AccessControlService(role_repository, token_service)
