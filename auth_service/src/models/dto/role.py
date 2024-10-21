from typing import List

from uuid import UUID

from auth_service.src.models.dto.common import BaseDto
from auth_service.src.models.dto.permission import PermissionDto


class RoleDto(BaseDto):
    id: UUID
    name: str
    permissions: List[PermissionDto]


class RoleCreate(BaseDto):
    name: str
    permission_ids: List[UUID] | None = None


class RoleResponse(BaseDto):
    name: str
