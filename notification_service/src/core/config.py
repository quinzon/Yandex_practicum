from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field(alias='PROJECT_NAME', default='auth')
    log_level: str = Field(alias='LOG_LEVEL', default='INFO')
    rabbitmq_url: str = Field(alias='RABBITMQ_URL', default='amqp://guest:guest@localhost/')

    exchange_name: str = Field(alias='RABBITMQ_EXCHANGE', default='notifications_exchange')
    delayed_exchange_name: str = Field(alias='RABBITMQ_DELAYED_EXCHANGE',
                                       default='delayed_exchange')

    queue_names: str = Field(alias='RABBITMQ_QUEUES', default='email,sms,push')
    prefix: str = Field(alias='RABBITMQ_PREFIX', default='notifications')
    max_priority: int = Field(alias='MAX_PRIORITY', default=10)
    auth_service_url: str = Field(..., alias='AUTH_SERVICE_URL')

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
    )

    def get_queue_list(self) -> list[str]:
        return [queue.strip() for queue in self.queue_names.split(',')]


settings = Settings()
