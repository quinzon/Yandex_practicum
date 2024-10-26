from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    postgres_host: str = Field(..., alias='POSTGRES_HOST')
    postgres_port: int = Field(..., alias='POSTGRES_PORT')
    postgres_user: str = Field(..., alias='POSTGRES_USER')
    postgres_password: str = Field(..., alias='POSTGRES_PASSWORD')
    postgres_schema: str = Field(..., alias='POSTGRES_SCHEMA')
    postgres_db: str = Field(..., alias='POSTGRES_DB')

    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field('6379', alias='REDIS_PORT')
    redis_db: int = Field('1', alias='REDIS_DB')
    service_url: str = Field('http://api:8001', alias='SERVICE_URL')
    env: str = Field('test', alias='ENV')

    model_config = SettingsConfigDict(
        env_file='.env.tests',
        extra='ignore',
        env_file_encoding='utf-8'
    )

    @property
    def database_url(self) -> str:
        return (f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}'
                f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}')


test_settings = TestSettings()
database_url = test_settings.database_url
