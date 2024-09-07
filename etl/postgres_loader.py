import backoff
import psycopg2
from psycopg2._psycopg import cursor as Cursor

from models import Movie

class PostgresLoader:

    def __init__(self, cursor: Cursor, pack_size: int):
        self.cursor = cursor
        self.pack_size = pack_size

    @backoff.on_exception(backoff.expo, (psycopg2.InterfaceError, psycopg2.OperationalError))
    def read_movies(self, sql: str, modified: str, filmwork_id: str):
        """
        Вычитывает из базы данных фильмы, которые изменены после сохранённого состояния. Для состояния используется
        время изменения сущности и id фильма. Возвращает фильмы и новое состояние.
        """
        self.cursor.execute(sql, (modified, modified, filmwork_id))
        while rows := self.cursor.fetchmany(self.pack_size):
            movies = list()
            for row in rows:
                movie = Movie.parse_obj(row)
                movies.append(movie)
            yield movies, rows[-1].get('modified', ''), rows[-1].get('id', '')
