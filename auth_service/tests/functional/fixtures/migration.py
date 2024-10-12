import pytest_asyncio
from alembic.config import Config
from alembic import command

from auth_service.tests.functional.settings import database_url


@pytest_asyncio.fixture(scope="session")
async def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")
