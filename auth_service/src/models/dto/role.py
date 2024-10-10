from typing import List

from uuid import UUID

from auth_service.src.models.dto.common import BaseDto
from auth_service.src.models.dto.permission import PermissionResponse


class RoleResponse(BaseDto):
    id: UUID
    name: str
    permissions: List[PermissionResponse]

    class Config:
        orm_mode = True
