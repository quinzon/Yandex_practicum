from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    project_name: str = Field(default='ugc_test', alias='PROJECT_NAME')
    mongo_url: str = Field(..., alias='MONGO_URL')
    mongo_db: str = Field(..., alias='MONGO_DB')
    auth_service_url: str = Field(..., alias='AUTH_SERVICE_URL')
    service_url: str = Field(..., alias='SERVICE_URL')
    env: str = Field(..., alias='ENV')

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


test_settings = TestSettings()
