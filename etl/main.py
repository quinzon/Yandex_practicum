from time import sleep

import backoff
import psycopg2
import requests
from psycopg2.extras import RealDictCursor

from postgres_loader import PostgresLoader
from settings import Settings
from es_uploader import ElasticSearchUploader
from state import State, JsonFileStorage


@backoff.on_exception(backoff.expo, (psycopg2.InterfaceError, psycopg2.OperationalError,
                                     requests.exceptions.ConnectionError))
def main(settings):
    try:
        with psycopg2.connect(dsn=settings.POSTGRES_DSN) as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
            loader = PostgresLoader(cursor, settings.PACK_SIZE)
            uploader = ElasticSearchUploader(settings.ES_URL, settings.ES_INDEX)
            for entity_key in settings.ENTITIES:
                entity = settings.ENTITIES[entity_key]
                state = State(JsonFileStorage(file_path=settings.FILE_STORAGE_PATH))
                modified = state.get_state(entity.modified_key)
                filmwork_id = state.get_state(entity.id_key)
                modified = modified if modified is not None else settings.START_TIME
                for movies, last_modified, last_id in loader.read_movies(entity.sql, modified, filmwork_id):
                    uploader.upload(movies)
                    state.set_state(entity.modified_key, str(last_modified))
                    state.set_state(entity.id_key, last_id)
    finally:
        conn.close()


if __name__ == '__main__':
    while True:
        settings = Settings()
        main(settings)
        sleep(settings.SLEEP_TIME)
