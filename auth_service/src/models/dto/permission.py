from uuid import UUID

from auth_service.src.models.dto.common import BaseDto


class PermissionCreate(BaseDto):
    name: str
    http_method: str
    resource: str


class PermissionDto(PermissionCreate):
    id: UUID


class PermissionUpdate(PermissionDto):
    id: UUID
