from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field(default='ugc', alias='PROJECT_NAME')
    mongo_url: str = Field(..., alias='MONGO_URL')
    redis_host: str = Field(..., alias='REDIS_HOST')
    redis_port: int = Field(..., alias='REDIS_PORT')
    redis_db: int = Field(..., alias='REDIS_DB')
    auth_service_url: int = Field(..., alias='AUTH_SERVICE_URL')

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


settings = Settings()
