import os
from functools import lru_cache
from logging import config as logging_config

from pydantic import Extra
from pydantic_settings import BaseSettings

from src.core.logger import LOGGING


logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RedisSettings(BaseSettings):
    host: str
    port: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "redis_"
        extra = Extra.ignore


class ElasticSearchSettings(BaseSettings):
    host: str
    port: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "elastic_"
        extra = Extra.ignore


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache()
def get_elastic_settings() -> ElasticSearchSettings:
    return ElasticSearchSettings()