from pydantic import Field, Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FLASK_ENV: str = Field('production', alias='FLASK_ENV')
    DEBUG: bool = Field(False, alias='FLASK_DEBUG')
    HOST: str = Field('0.0.0.0', alias='APP_HOST')
    PORT: int = Field(5000, alias='APP_PORT')

    KAFKA_BROKER_URLS: str = Field('localhost:9092', alias='KAFKA_BROKER_URLS')

    SECRET_KEY: str = Field('default-secret-key', alias='SECRET_KEY')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.ignore


settings = Settings()
