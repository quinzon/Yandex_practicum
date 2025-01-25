import os
from functools import lru_cache
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from push_service.src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class GlobalSettings(CommonSettings):
    project_name: str = Field(alias='PROJECT_NAME', default='push')
    auth_service_url: str = Field(alias='AUTH_SERVICE_URL', default='http://auth_service:8001/api/v1/auth')


class RedisSettings(CommonSettings):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')
    db: int = Field(..., alias='REDIS_DB')

    model_config = SettingsConfigDict(
        env_prefix='redis_',
    )

    def redis_url(self) -> str:
        return f'redis://{self.host}:{self.port}/{self.db}'


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache()
def get_global_settings() -> GlobalSettings:
    return GlobalSettings()
