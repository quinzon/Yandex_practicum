import uuid
from abc import abstractmethod
from typing import TypeVar, Generic, List, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError


T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    def get_model(self) -> Type[T]:
        pass

    async def get_all(
        self, page: int = 1, page_size: int = 10
    ) -> List[T]:
        query = select(T).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, entity_id: uuid) -> T | None:
        return await self.session.get(self.get_model(), entity_id)
    
    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.commit()

    async def get_id_by_name(self, name: str) -> Optional[uuid.UUID]:
        model=self.get_model()
        result = await self.session.execute(select(model).filter(model.name == name))
        entity = result.scalars().first()
        return entity.id if entity else None
    
    async def get_by_name(self, name: str) -> T | None:
        id = await self.get_id_by_name(name)
        return await self.get_by_id(id)
    