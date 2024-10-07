from typing import List

from pydantic import BaseModel
from uuid import UUID

from auth_service.src.models.dto.permission import PermissionResponse


class RoleResponse(BaseModel):
    id: UUID
    name: str
    permissions: List[PermissionResponse]

    class Config:
        orm_mode = True
