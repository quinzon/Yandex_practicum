from pydantic import BaseSettings, BaseModel, PostgresDsn

from sql_queries import MOVIES_SQL_BY_MODIFIED_MOVIES
import os

class EntityParams(BaseModel):
    sql: str
    modified_key: str
    id_key: str


class Settings(BaseSettings):
    POSTGRES_DSN: PostgresDsn
    ES_URL: str
    ES_INDEX = 'movies'

    PACK_SIZE = 500
    FILE_STORAGE_PATH = 'app_state.json'
    START_TIME = '1900-01-01 00:00:00'
    SLEEP_TIME = 600
    ENTITIES: dict[str, EntityParams] = {
        'film_work': EntityParams(
            sql=MOVIES_SQL_BY_MODIFIED_MOVIES,
            modified_key='filmwork_modified',
            id_key='filmwork_id'),
        'genre': EntityParams(
            sql=MOVIES_SQL_BY_MODIFIED_MOVIES,
            modified_key='genre_modified',
            id_key='genre_filmwork_id'),
        'person': EntityParams(
            sql=MOVIES_SQL_BY_MODIFIED_MOVIES,
            modified_key='person_modified',
            id_key='person_filmwork_id')
    }

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        fields = {
            'POSTGRES_DSN': {
                'env': 'POSTGRES_DSN',
            },
            'ES_URL': {
                'env': 'ES_URL',
            },
        }