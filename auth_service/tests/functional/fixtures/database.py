import pytest_asyncio
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from auth_service.tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clear_db():
    """
    Clean database before each test.
    """
    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # getting all tables
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'auth';
    """)
    tables = cur.fetchall()

    for table in tables:
        cur.execute(f'TRUNCATE TABLE "auth"."{table[0]}" RESTART IDENTITY CASCADE')

    cur.close()
    conn.close()
