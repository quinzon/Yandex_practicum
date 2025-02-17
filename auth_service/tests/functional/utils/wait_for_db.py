import asyncio

import asyncpg

from auth_service.tests.functional.settings import test_settings
from auth_service.tests.functional.utils.backoff import backoff
from auth_service.tests.functional.utils.logger import logger


@backoff(start_sleep_time=0.5, factor=2, border_sleep_time=10)
async def wait_for_postgres():
    try:
        conn = await asyncpg.connect(
            host=test_settings.postgres_host,
            port=test_settings.postgres_port,
            user=test_settings.postgres_user,
            password=test_settings.postgres_password,
            database=test_settings.postgres_db
        )
        await conn.execute('SELECT 1')
        await conn.close()
        logger.debug('PostgreSQL is available!')
        return True
    except Exception as e:
        logger.debug(f'Waiting for PostgreSQL... Error: {e}')
        raise Exception('Waiting for PostgreSQL...')


if __name__ == '__main__':
    asyncio.run(wait_for_postgres())
