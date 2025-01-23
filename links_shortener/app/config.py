from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str  # Имя пользователя PostgreSQL
    POSTGRES_PASSWORD: str  # Пароль для PostgreSQL
    POSTGRES_SQL_DB: str  # Имя базы данных (оставляю как в вашем примере)
    POSTGRES_HOST: str = "postgres"  # Хост базы данных, по умолчанию "postgres"
    POSTGRES_PORT: int = 5432  # Порт для подключения к PostgreSQL
    BASE_URL: str = "http://localhost/api/v1/shortener"  # Базовый URL API

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_SQL_DB}")

    class Config:
        env_file = ".env"  # Путь к файлу с переменными окружения


# Создаем экземпляр настроек
settings = Settings()
