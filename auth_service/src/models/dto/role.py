from typing import List
from uuid import UUID

from pydantic import BaseModel

from auth_service.src.models.dto.common import BaseDto
from auth_service.src.models.dto.permission import PermissionResponse

class RoleCreate(BaseModel):
    name: str

class Role(BaseModel):
    name: str

class RoleResponse(BaseDto):
    id: UUID
    name: str
    permissions: List[str]

    class Config:
        orm_mode = True

class RoleNestedResponse(BaseDto):
    id: UUID
    name: str
    permissions: List[PermissionResponse]

    class Config:
        orm_mode = True