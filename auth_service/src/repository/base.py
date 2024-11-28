import uuid
from abc import abstractmethod
from http import HTTPStatus
from typing import TypeVar, Generic, List, Type, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    def get_model(self) -> Type[T]:
        pass

    async def get_all(self, page: int = 1, page_size: int = 10) -> Tuple[List[T], int]:
        model = self.get_model()
        query = select(model).offset((page - 1) * page_size).limit(page_size)
        total_query = select(func.count()).select_from(model)
        try:
            result = await self.session.execute(query)
            total_result = await self.session.execute(total_query)
            total_items = total_result.scalar_one()
            return result.scalars().all(), total_items
        except SQLAlchemyError:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Failed to fetch records'
            )

    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        try:
            result = await self.session.get(self.get_model(), entity_id)
            if not result:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f'Record with ID {entity_id} not found'
                )
            return result
        except SQLAlchemyError:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Internal server error'
            )

    async def create(self, entity: T) -> T:
        try:
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Already exists'
            )
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Internal server error'
            )

    async def update(self, entity: T) -> T:
        try:
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Update conflict'
            )
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Internal server error'
            )

    async def delete(self, entity: T) -> None:
        try:
            await self.session.delete(entity)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Failed to delete entity'
            )
