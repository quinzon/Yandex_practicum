import time
from datetime import datetime
from typing import Generator, Any, Type, Callable

import pytz
from dateutil import parser
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Document

from documents.movie import Movie, get_movie_index_data
from documents.person import Person, get_person_index_data
from documents.genre import Genre, get_genre_index_data
from helpers.backoff_func_wrapper import backoff
from logger import logger
from settings import settings
from state_manager.json_file_storage import JsonFileStorage
from state_manager.state_manager import StateManager


DataLoader = Callable[[dict, datetime, int], Generator[list[Type[Document]], None, None]]

@backoff(0.1, 2, 10, logger)
def _send_to_es(es_load_data:  Generator[dict[str, Any], Any, None]):
    bulk(
        connections.get_connection(),
        es_load_data,
    )


def update_index(state_name: str, es_model: Type[Document], get_data_function: DataLoader):
    state_manager = StateManager(JsonFileStorage(logger=logger))

    last_sync_state = state_manager.get_state(state_name)

    if last_sync_state is None:
        last_sync_state = pytz.UTC.localize(datetime.min)
    else:
        last_sync_state = parser.isoparse(last_sync_state)

    connections.create_connection(hosts=settings.elasticsearch_settings.get_host())

    es_model.init()

    for rows in get_data_function(settings.database_settings.get_dsn(), last_sync_state, 100):
        es_load_data = (dict(d.to_dict(True, skip_empty=False), **{'_id': d.id}) for d in rows)

        _send_to_es(es_load_data)

        last_change_date = pytz.UTC.localize(max(item.last_change_date for item in rows))
        if last_change_date > last_sync_state:
            last_sync_state = last_change_date

    state_manager.set_state(state_name, last_sync_state.isoformat())


if __name__ == '__main__':
    while True:
        try:
            update_index('person_index_last_sync_state', Person, get_person_index_data)
            update_index('movie_index_last_sync_state', Movie, get_movie_index_data)
            update_index('genre_index_last_sync_state', Genre, get_genre_index_data)
            time.sleep(60)
        except Exception as e:
            logger.exception(e)
