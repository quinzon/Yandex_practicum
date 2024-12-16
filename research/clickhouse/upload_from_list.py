import time
import uuid
import multiprocessing as mp

import docker

from clickhouse_driver import Client
from faker import Faker


client = Client(host='localhost')
docker_client = docker.from_env()
fake: Faker = Faker()
num_chunks = 1000
chunk_size = 10_000


def load_data(size):
    start = time.time()

    lines = [(uuid.uuid4(),
              uuid.uuid4(),
              fake.random_int(min=0, max=1000),
              fake.date_time_between(start_date='-1y', end_date='now'))
             for _ in range(size)]

    end = time.time()

    return lines, end - start


def prepare_db():
    client.execute(
        """
        DROP TABLE IF EXISTS user_viewed_frame;
        """
    )
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS user_viewed_frame
        (
            user_id UUID,
            film_id UUID,
            viewed_frame Int64,
            ts DateTime
        ) engine=MergeTree()
        ORDER BY (user_id, film_id, viewed_frame);
        """
    )


lines, elapsed_time_create_lines = load_data(chunk_size)
if elapsed_time_create_lines:
    print(f"Upload chunk_size={chunk_size} rows to list in "
          f"{elapsed_time_create_lines} seconds", flush=True)


def insert_data(chunks_amount=None) -> None:
    try:
        client.execute(
            "INSERT INTO user_viewed_frame "
            "(user_id, film_id, viewed_frame, ts) VALUES",
            lines,
        )
    except Exception as err:
        print(err)


if __name__ == "__main__":

    total_records = num_chunks * chunk_size

    prepare_db()

    start_time = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(insert_data, range(num_chunks))

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Insert {total_records} (num_chunks={num_chunks}, "
          f"chunk_size={chunk_size}) rows in "
          f"{elapsed_time} seconds")
    insertion_speed = total_records / elapsed_time
    print(f"Insert speed: {insertion_speed} rows/sec")
    print(f"Total time: {elapsed_time} sec")
