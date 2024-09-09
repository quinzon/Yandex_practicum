from pydantic import Field, Extra
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    host: str = Field(..., alias='POSTGRES_HOST')
    port: int = Field(..., alias='POSTGRES_PORT')
    dbname: str = Field(..., alias='POSTGRES_SQL_DB')
    user: str = Field(..., alias='POSTGRES_USER')
    password: str = Field(..., alias='POSTGRES_PASSWORD')

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = Extra.ignore

    def get_dsn(self) -> dict:
        return self.model_dump()


class ElasticsearchSettings(BaseSettings):
    host: str = Field(..., alias='ES_HOST')
    port: str = Field(..., alias='ES_PORT')

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = Extra.ignore

    def get_host(self):
        return f'{self.host}:{self.port}'


class Settings(BaseSettings):
    # debug: bool = Field(..., alias='DEBUG')
    debug: bool = Field(True, alias='DEBUG')
    database_settings: DatabaseSettings = DatabaseSettings()
    elasticsearch_settings: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()
