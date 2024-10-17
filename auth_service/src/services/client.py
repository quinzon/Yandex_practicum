from functools import lru_cache
from typing import List,Optional
from http import HTTPStatus
import asyncio

from fastapi import Depends, HTTPException
#from fastapi.security import OAuth2PasswordBearer

from auth_service.src.models.dto.role import RoleCreate, RoleResponse
from auth_service.src.repository.role import RoleRepository, get_role_repository
from auth_service.src.models.entities.role import Role
from auth_service.src.services.token import get_token_service

#from auth_service.src.services.role import get_role_service

class ClientService:
    '''def __init__(self, token: str,token_service ):
        self.token = token
        self.token_service = token_service'''

    def __init__(self, token_service ):
        self.token_service = token_service

    def set_token(self, token: str ):
        self.token = token
        
    async def populate_permissions(self):
        assert self.token
        print(25,self.token,self.token_service.settings)
        token_data=await self.token_service.get_token_data(self.token)
        self.roles = token_data.roles
        # get unique permissions
        permissions = {}
        for role in self.roles:
            permissions.update(role.get_role_permissions())
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

'''@lru_cache()
def get_client_service(token: Optional[str],
    token_service=Depends(get_token_service)
    ) -> ClientService:
    return ClientService(token,token_service)'''

@lru_cache()
def get_client_service(
        token_service=Depends(get_token_service)
    ) -> ClientService:
    return ClientService(token_service)