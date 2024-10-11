from uuid import UUID

from pydantic import BaseModel

from auth_service.src.models.dto.common import BaseDto

class Permission(BaseModel):
    name: str

class PermissionResponse(BaseDto):
    id: UUID
    name: str

    class Config:
        orm_mode = True
