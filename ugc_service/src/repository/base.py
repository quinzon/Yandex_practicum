from typing import List, Optional, Dict, Any, TypeVar, Generic
from uuid import UUID
from beanie import Document, SortDirection
from abc import ABC, abstractmethod

T = TypeVar('T', bound=Document)


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_model(self) -> T:
        pass

    async def create(self, item: T) -> T:
        await item.insert()
        return item

    async def get(self, item_id: UUID) -> Optional[T]:
        model = self.get_model()
        return await model.find_one({'_id': item_id})

    async def update(self, item_id: UUID, item: T) -> Optional[T]:
        existing_item = await self.get(item_id)
        if not existing_item:
            return None
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_item, key, value)
        await existing_item.save()
        return existing_item

    async def delete(self, item_id: UUID) -> None:
        model = self.get_model()
        await model.find_one({'_id': item_id}).delete()

    async def find(
            self,
            filters: Dict[str, Any],
            skip: int = 0,
            limit: int = 10,
            sort_by: Optional[Dict[str, int]] = None,
    ) -> List[T]:
        model = self.get_model()
        query = model.find(filters)

        if sort_by:
            sort_params = [
                (field, SortDirection.ASCENDING if direction == 1 else SortDirection.DESCENDING)
                for field, direction in sort_by.items()
            ]
            query = query.sort(*sort_params)

        return await query.skip(skip).limit(limit).to_list()
