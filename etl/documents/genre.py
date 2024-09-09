from datetime import datetime
from typing import Generator

import psycopg
from elasticsearch_dsl import (
    Document,
    Keyword,
    MetaField,
    Text,
)
from psycopg import ServerCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row


class Genre(Document):
    id = Keyword()
    name = Text(analyzer='ru_en')
    description = Text(analyzer='ru_en')

    class Index:
        name = 'genres'
        settings = {
            'refresh_interval': '1s',
            'analysis': {
                'filter': {
                    'english_stop': {'type': 'stop', 'stopwords': '_english_'},
                    'english_stemmer': {'type': 'stemmer', 'language': 'english'},
                    'russian_stop': {'type': 'stop', 'stopwords': '_russian_'},
                    'russian_stemmer': {'type': 'stemmer', 'language': 'russian'},
                },
                'analyzer': {
                    'ru_en': {
                        'tokenizer': 'standard',
                        'filter': [
                            'lowercase',
                            'english_stop',
                            'english_stemmer',
                            'russian_stop',
                            'russian_stemmer',
                        ],
                    }
                },
            },
        }

    class Meta:
        dynamic = MetaField('strict')


def get_genre_index_data(
        database_settings: dict, last_sync_state: datetime, batch_size: int = 100
) -> Generator[list[Genre], None, None]:
    dsn = make_conninfo(**database_settings)

    with psycopg.connect(dsn, row_factory=dict_row) as conn, ServerCursor(conn, 'fetcher') as cursor:
        raw_sql = """
        SELECT
            g.id,
            g.name,
            g.description,
            max(v.last_change_date) as last_change_date
        FROM content.genre g
        cross join lateral (values (g.updated_at)) v(last_change_date)
        GROUP BY g.id
        having max(v.last_change_date) > %s
        ORDER BY g.updated_at
        """
        cursor.execute(raw_sql, (last_sync_state,))

        while results := cursor.fetchmany(size=batch_size):
            genres = []
            for result in results:
                genre = Genre(
                    id=result['id'],
                    name=result['name'],
                    description=result.get('description', None)
                )
                genres.append(genre)

            yield genres
