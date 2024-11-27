import os
from functools import lru_cache
from logging import config as logging_config
from typing import Dict

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

from auth_service.src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUPPORTED_OAUTH_PROVIDERS = ['yandex',]


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class GlobalSettings(CommonSettings):
    session_secret_key: str = Field(alias='SESSION_SECRET_KEY')
    project_name: str = Field(alias='PROJECT_NAME', default='auth')
    rate_limit: str = Field(alias='RATE_LIMIT', default='10/minute')
    env: str = Field(alias='ENV', default='development')


class JWTSettings(CommonSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    def __hash__(self):
        return hash(
            (
                self.secret_key, self.algorithm,
                self.access_token_expire_minutes,
                self.refresh_token_expire_minutes
            )
        )


class RedisSettings(CommonSettings):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')
    db: int = Field(..., alias='REDIS_DB')

    model_config = SettingsConfigDict(
        env_prefix='redis_',
    )

    def redis_url(self) -> str:
        return f'redis://{self.host}:{self.port}/{self.db}'


class PostgresSettings(CommonSettings):
    host: str = Field(..., alias='POSTGRES_HOST')
    port: int = Field(..., alias='POSTGRES_PORT')
    user: str = Field(..., alias='POSTGRES_USER')
    password: str = Field(..., alias='POSTGRES_PASSWORD')
    schema: str = Field(..., alias='POSTGRES_SCHEMA')
    db: str = Field(..., alias='POSTGRES_DB')
    echo: bool = Field(default=False, alias='POSTGRES_ECHO')

    model_config = SettingsConfigDict(
        env_prefix='postgres_',
    )

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class OAuthProviderSettings(CommonSettings):
    client_id: str
    client_secret: str
    authorize_url: str
    access_token_url: str
    scope: str
    userinfo_endpoint: str


class OAuthSettings(CommonSettings):
    providers: Dict[str, OAuthProviderSettings] = {}

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
    )

    @classmethod
    def load_from_env(cls) -> 'OAuthSettings':
        settings = cls()
        for provider_name in SUPPORTED_OAUTH_PROVIDERS:
            prefix = f'{provider_name.upper()}_'
            provider_settings = OAuthProviderSettings(
                client_id=os.getenv(f'{prefix}CLIENT_ID'),
                client_secret=os.getenv(f'{prefix}CLIENT_SECRET'),
                authorize_url=os.getenv(f'{prefix}AUTHORIZE_URL'),
                access_token_url=os.getenv(f'{prefix}ACCESS_TOKEN_URL'),
                scope=os.getenv(f'{prefix}SCOPE', ''),
                userinfo_endpoint=os.getenv(f'{prefix}USERINFO_ENDPOINT'),
            )
            settings.providers[provider_name] = provider_settings
        return settings


class JaegerSettings(CommonSettings):
    host: str = Field(..., alias='JAEGER_HOST')
    port: int = Field(..., alias='JAEGER_PORT')


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache()
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings()


@lru_cache()
def get_postgres_url() -> str:
    settings = get_postgres_settings()
    return settings.database_url


@lru_cache()
def get_jwt_settings() -> JWTSettings:
    return JWTSettings()


@lru_cache()
def get_jaeger_settings() -> JaegerSettings:
    return JaegerSettings()


@lru_cache()
def get_oauth_settings() -> OAuthSettings:
    return OAuthSettings().load_from_env()


@lru_cache()
def get_global_settings() -> GlobalSettings:
    return GlobalSettings()
