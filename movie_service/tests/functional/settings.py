from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.functional.testdata.genres_index import GENRES_INDEX
from tests.functional.testdata.movies_index import MOVIES_INDEX
from tests.functional.testdata.persons_index import PERSONS_INDEX


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1', alias='ES_HOST')
    es_port: str = Field('9200', alias='ES_PORT')
    es_genre_index: str = Field('genres', alias='ES_GENRE_INDEX')
    es_movie_index: str = Field('movies', alias='ES_MOVIE_INDEX')
    es_persons_index: str = Field('persons', alias='ES_PERSON_INDEX')
    es_movies_index_mapping: dict = MOVIES_INDEX
    es_persons_index_mapping: dict = PERSONS_INDEX
    es_genres_index_mapping: dict = GENRES_INDEX

    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field("6379", alias='REDIS_PORT')
    service_url: str = Field('http://api:8000', alias='SERVICE_URL')

    model_config = SettingsConfigDict(
        env_file='.env.tests',
        extra='ignore',
        env_file_encoding='utf-8'
    )


test_settings = TestSettings()
