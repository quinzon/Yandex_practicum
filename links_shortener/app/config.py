from dotenv import load_dotenv
import os

class Config:
    load_dotenv()
    POSTGRES_USER = os.getenv("POSTGRES_SH_USER")  # Добавить переменную для пользователя
    POSTGRES_PASSWORD = os.getenv("POSTGRES_SH_PASSWORD")  # Добавить переменную для пароля
    POSTGRES_DB = os.getenv("POSTGRES_SH_DB")  # Добавить переменную для имени базы данных
    POSTGRES_HOST = os.getenv("POSTGRES_SH_HOST", "postgres_sh")  # Это адрес базы данных
    POSTGRES_PORT = os.getenv("POSTGRES_SH_PORT", 5432)  # Порт базы данных (по умолчанию 5433)

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8001/")
