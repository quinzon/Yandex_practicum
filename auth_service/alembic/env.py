import re
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from auth_service.src.core.config import get_postgres_url
from auth_service.src.db.postgres import Base
from auth_service.src.models.entities import import_all_models

config = context.config
fileConfig(config.config_file_name)
import_all_models()
target_metadata = Base.metadata

DATABASE_URL = get_postgres_url()


def run_migrations_online():
    sync_url = DATABASE_URL.replace('+asyncpg', '')
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        url=sync_url,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def include_object(object, name, type_, reflected, compare_to):
        # Исключаем таблицы-партиции по шаблону "tablename_YYYY_MM", но сохраняем саму "login_history"
        partition_regex = re.compile(r'login_history_\d{4}_\d{2}$')

        # Включаем только таблицы из схемы "auth", исключая партиции
        if type_ == "table" and object.schema == 'auth' and not partition_regex.search(name):
            return True
        # Исключаем все остальные объекты
        return False

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
