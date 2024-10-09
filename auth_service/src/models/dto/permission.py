from uuid import UUID

from auth_service.src.models.dto.common import BaseDto


class PermissionResponse(BaseDto):
    id: UUID
    name: str

    class Config:
        orm_mode = True
