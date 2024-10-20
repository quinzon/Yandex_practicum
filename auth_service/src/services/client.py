from functools import lru_cache
from typing import List,Optional
from http import HTTPStatus

from fastapi import Depends, HTTPException

from auth_service.src.repository.role import get_role_repository
from auth_service.src.services.token import get_token_service

class Client:
    def __init__(self, token_service, role_repository ):
        self.token_service = token_service
        self.role_repository = role_repository

    def set_token(self, token: str ):
        self.token = token
        
    async def populate_permissions(self):
        assert self.token
        token_data=await self.token_service.get_token_data(self.token)
        self.roles = token_data.roles
        
        roles = [await self.role_repository.get_by_name(name) for name in self.roles]
        # get unique permissions
        permissions = set()
        for role in roles:
            permissions_names = [perm.name for perm in role.permissions]
            permissions.update(set(permissions_names))
        self.permissions = tuple(permissions)

    async def has_permission(self, required_permission: str) -> bool:
        await self.populate_permissions()
        if required_permission in self.permissions:
            return True
        else:
            raise HTTPException(
                        status_code=HTTPStatus.FORBIDDEN,
                        detail=f"No {required_permission} permission."
                    )        

@lru_cache()
def get_client(
        token_service=Depends(get_token_service),
        role_repository=Depends(get_role_repository)
    ) -> Client:
    return Client(token_service, role_repository)
