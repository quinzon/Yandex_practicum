from dotenv import load_dotenv
import os


class Config:
    load_dotenv()
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_SQL_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

    SQLALCHEMY_DATABASE_URI = (f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
                               f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8001/")
