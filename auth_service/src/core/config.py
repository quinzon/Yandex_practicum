import os
from functools import lru_cache
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from auth_service.src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'auth')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class JWTSettings(CommonSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    def __hash__(self):
        return hash(
            (self.secret_key, self.algorithm, self.access_token_expire_minutes, self.refresh_token_expire_minutes))


class RedisSettings(CommonSettings):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')

    model_config = SettingsConfigDict(
        env_prefix='redis_',
    )


class PostgresSettings(CommonSettings):
    host: str = Field(..., alias='POSTGRES_HOST')
    port: int = Field(..., alias='POSTGRES_PORT')
    user: str = Field(..., alias='POSTGRES_USER')
    password: str = Field(..., alias='POSTGRES_PASSWORD')
    schema: str = Field(..., alias='POSTGRES_SCHEMA')
    db: str = Field(..., alias='POSTGRES_DB')

    model_config = SettingsConfigDict(
        env_prefix='postgres_',
    )

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache()
def get_postgres_settings() -> PostgresSettings:
    s=PostgresSettings()
    print(70,s)
    return s


@lru_cache()
def get_postgres_url() -> str:
    settings = get_postgres_settings()
    return settings.database_url


@lru_cache()
def get_jwt_settings() -> JWTSettings:
    return JWTSettings()
