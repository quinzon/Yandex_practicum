from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rabbitmq_url: str = Field(alias='RABBITMQ_URL')
    auth_service_url: str = Field(alias='AUTH_SERVICE')
    admin_service_url: str = Field(alias='ADMIN_SERVICE')
    push_service_url: str = Field(alias='PUSH_SERVICE')
    sendgrid_email_key: str = Field(alias='SENDGRID_EMAIL_KEY')
    email_from: str = Field(alias='EMAIL_FROM')

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
    )


settings = Settings()
