import os
from functools import lru_cache
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from movie_service.src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RedisSettings(BaseSettings):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='redis_',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class ElasticSearchSettings(BaseSettings):
    host: str = Field(..., alias='ES_HOST')
    port: int = Field(..., alias='ES_PORT')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='es_',
        extra='ignore',
        env_file_encoding='utf-8'
    )


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache()
def get_elastic_settings() -> ElasticSearchSettings:
    return ElasticSearchSettings()
