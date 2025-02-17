import logging

from alembic.config import Config
from alembic import command

from auth_service.tests.functional.settings import database_url
from auth_service.tests.functional.utils.backoff import backoff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@backoff(start_sleep_time=0.5, factor=2, border_sleep_time=10)
def apply_migrations():
    alembic_cfg = Config('/opt/auth_service/alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', database_url)
    alembic_cfg.set_main_option('script_location', '/opt/auth_service/alembic')

    try:
        logger.info('Applying database migrations...')
        command.upgrade(alembic_cfg, 'head')
        logger.info('Migrations applied successfully.')
        return True
    except Exception as e:
        logger.error(f'Error applying migrations: {e}')
        raise


if __name__ == '__main__':
    apply_migrations()
