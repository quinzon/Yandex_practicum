import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import  declarative_base
from auth_service.tests.functional.settings import database_url


engine = create_async_engine(database_url, future=True, echo=True)
Base = declarative_base()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def test_db():
    print('hi')

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
