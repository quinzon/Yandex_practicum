from pydantic import Field, Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    flask_env: str = Field('production', alias='FLASK_ENV')
    debug: bool = Field(False, alias='FLASK_DEBUG')
    host: str = Field('0.0.0.0', alias='APP_HOST')
    port: int = Field(5000, alias='APP_PORT')

    kafka_broker_urls: str = Field('localhost:9092', alias='KAFKA_BROKER_URLS')

    secret_key: str = Field('default-secret-key', alias='SECRET_KEY')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.ignore


settings = Settings()
