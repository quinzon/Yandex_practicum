import time
import vertica_python

import multiprocessing as mp
from vertica.upload import insert_data

conn_info = {
    "host": "localhost",
    "port": 5433,
    "user": "dbadmin",
    "password": "",
    "database": "docker",
    "autocommit": True,
}
conn = vertica_python.connect(**conn_info)
cursor = conn.cursor()


def read_data():
    try:
        cursor.execute(
            """
        SELECT
            user_id,
            max(viewed_frame)
        FROM user_viewed_frame
        WHERE ts > '2022-12-01 00:00:00'
        GROUP by user_id
        """
        )
        cursor.fetchall()
    except Exception as err:
        print(err)


if __name__ == "__main__":
    start_time = time.time()
    p1_upload = mp.Process(target=insert_data)
    p1_upload.start()

    p2_read = mp.Process(target=read_data)
    p2_read.start()

    p1_upload.join()
    p2_read.join()

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Select all rows in {elapsed_time} seconds")

    cursor.close()
    conn.close()
