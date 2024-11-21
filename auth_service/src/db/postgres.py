from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker

from auth_service.src.core.config import get_postgres_settings

metadata_obj = MetaData(schema='auth')
Base = declarative_base(metadata=metadata_obj)


def create_engine() -> AsyncEngine:
    settings = get_postgres_settings()
    dsn = f'postgresql+asyncpg://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.db}'
    return create_async_engine(dsn, echo=settings.echo, future=True)


engine = create_engine()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
