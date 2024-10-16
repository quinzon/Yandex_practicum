from functools import lru_cache
from typing import List
from http import HTTPStatus

from fastapi import Depends, HTTPException

#from auth_service.src.models.dto.role import RoleCreate, RoleResponse
from auth_service.src.repository.permission import PermissionRepository, get_permission_repository
from auth_service.src.models.entities.permission import Permission
from auth_service.src.services.base import BaseService

class PermissionService(BaseService[Permission]):
    pass

@lru_cache()
def get_permission_service(
    permission_repository: PermissionRepository = Depends(get_permission_repository)
) -> PermissionService:
    return PermissionService(permission_repository)
