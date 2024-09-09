from datetime import datetime
from typing import Generator

import psycopg
from elasticsearch_dsl import Document, Keyword, Text, InnerDoc, Nested
from psycopg import ServerCursor
from psycopg.conninfo import make_conninfo
from psycopg.rows import class_row, dict_row


class Film(InnerDoc):
    id = Keyword()
    roles = Keyword()


class Person(Document):
    id = Keyword()
    full_name = Text(analyzer='ru_en')
    films = Nested(Film)
    last_change_date = Keyword(index=False)

    class Index:
        name = 'persons'
        settings = {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    "russian_stemmer": {"type": "stemmer", "language": "russian"}
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                    }
                }
            }
        }


def get_person_index_data(
        database_settings: dict, last_sync_state: datetime, batch_size: int = 100
) -> Generator[list[Person], None, None]:
    dsn = make_conninfo(**database_settings)

    with psycopg.connect(dsn, row_factory=dict_row) as conn, ServerCursor(conn, 'fetcher') as cursor:
        raw_sql = '''
        WITH person_film_work_details AS (
            SELECT
                p.id AS person_id,
                p.full_name as person_full_name,
                pfw.film_work_id AS film_id,
                pfw.role,
                max(v.last_change_date) AS last_change_date
            FROM
                content.person p
                JOIN content.person_film_work pfw ON p.id = pfw.person_id
                JOIN content.film_work fw ON pfw.film_work_id = fw.id
                cross join lateral (values (fw.updated_at), (pfw.created_at), (p.updated_at)) v(last_change_date)
            GROUP BY p.id, film_work_id, pfw.role
            having max(v.last_change_date) > %s
        ),
        film_roles AS (
            SELECT
                person_id,
                film_id,
                person_full_name,
                ARRAY_AGG(role) AS roles,
                MAX(last_change_date) AS last_change_date
            FROM
                person_film_work_details
            GROUP BY
                person_id, film_id, person_full_name
        )
        SELECT
            person_id,
            person_full_name,
            JSON_AGG(
                JSON_BUILD_OBJECT(
                    'id', film_id,
                    'roles', roles
                )
            ) AS films,
            MAX(last_change_date) as last_change_date
        FROM
            film_roles
        GROUP BY
            person_id, person_full_name
        '''
        cursor.execute(raw_sql, params=(last_sync_state,))

        while results := cursor.fetchmany(size=batch_size):
            persons = []
            for result in results:
                person = Person(
                    id=result['person_id'],
                    full_name=result['person_full_name'],
                    films=[Film(id=film['id'], roles=film['roles']) for film in result['films']],
                    last_change_date=result['last_change_date']
                )
                persons.append(person)
            yield persons
