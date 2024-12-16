import os
import tarfile
import time
import uuid
import multiprocessing as mp

import docker

from clickhouse_driver import Client
from faker import Faker


client = Client(host='localhost')
docker_client = docker.from_env()
fake: Faker = Faker()


def load_data_to_file(size):
    filename = 'data.csv'

    start = time.time()

    lines = ((f"'{uuid.uuid4()}',"
              f"'{uuid.uuid4()}',"
              f"{fake.random_int(min=0, max=1000)},"
              f"'{fake.date_time_between(start_date='-1y', end_date='now')}'"
              f"\n")
             for _ in range(size))
    with open(filename, 'w') as file:
        file.write(''.join(str(x) for x in lines))
    end = time.time()

    with tarfile.open(f'{filename}' + '.tar', mode='w') as tar:
        tar.add(f'{filename}')

    return end - start


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


def insert_data(chunks_amount=None) -> None:
    if not os.path.isfile(f'{os.getcwd()}/data.csv'):
        raise Exception('Create data.csv first!')
    try:
        client.execute(
            "INSERT INTO user_viewed_frame "
            "SELECT * FROM file("
            "'data.csv', "
            "'CSV', "
            "'user_id UUID, film_id UUID, viewed_frame Int64, ts DateTime');"
            )
    except Exception as err:
        print(err)


if __name__ == "__main__":
    num_chunks = 10000
    chunk_size = 1000
    total_records = num_chunks * chunk_size

    prepare_db()

    elapsed_time_upload_to_file = load_data_to_file(chunk_size)
    if elapsed_time_upload_to_file:
        s = f"Upload chunk_size={chunk_size} rows to file in {elapsed_time_upload_to_file} seconds"
        print(s)

    container = docker_client.containers.get('clickhouse')
    container.put_archive('/var/lib/clickhouse/user_files/', open(
        f'{os.getcwd()}/data.csv.tar',
        'rb').read())

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
    print(f"Total time: {elapsed_time + elapsed_time_upload_to_file} sec")

    print(s)
