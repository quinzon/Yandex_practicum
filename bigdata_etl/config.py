from pydantic import Field, Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    clickhouse_host: str = Field(..., alias='CLICKHOUSE_HOST')
    kafka_broker: str = Field(..., alias='KAFKA_BROKER')
    poll_interval: float = Field(..., alias='POLL_INTERVAL')
    memory_log_interval: float = Field(..., alias='MEMORY_LOG_INTERVAL')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.ignore


settings = Settings()
