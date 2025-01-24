from pydantic import Field, Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    flask_env: str = Field('production', alias='FLASK_ENV')
    debug: bool = Field(False, alias='FLASK_DEBUG')
    host: str = Field('0.0.0.0', alias='APP_HOST')
    port: int = Field(5000, alias='APP_PORT')

    secret_key: str = Field('default-secret-key', alias='SECRET_KEY')

    redis_host: str = Field(..., alias='REDIS_HOST')
    redis_port: int = Field(..., alias='REDIS_PORT')
    redis_db: int = Field(..., alias='REDIS_DB')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.ignore


settings = Settings()
