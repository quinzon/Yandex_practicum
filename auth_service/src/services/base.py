import uuid
from typing import Generic, TypeVar, List, Tuple

from auth_service.src.repository.base import BaseRepository

T = TypeVar('T')


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    async def get_all(self, page: int = 1, page_size: int = 10) -> Tuple[List[T], int]:
        return await self.repository.get_all(page, page_size)

    async def get_by_id(self, entity_id: uuid) -> T | None:
        return await self.repository.get_by_id(entity_id)

    async def create(self, entity: T) -> T:
        return await self.repository.create(entity)

    async def update(self, entity: T) -> T:
        return await self.repository.update(entity)

    async def delete(self, entity: T) -> None:
        await self.repository.delete(entity)
