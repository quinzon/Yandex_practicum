from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field(default='ugc', alias='PROJECT_NAME')
    mongo_url: str = Field(..., alias='MONGO_URL')
    mongo_db: str = Field(..., alias='MONGO_DB')
    auth_service_url: str = Field(..., alias='AUTH_SERVICE_URL')

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


settings = Settings()
