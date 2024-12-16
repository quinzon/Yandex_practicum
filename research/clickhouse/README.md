# Загрузка данных в Clickhouse

1. `cd clickhouse`
2. `docker-compose up`
3. `python upload_from_file.py`

Здесь используется метод SELECT * FROM file для загрузки данных в ClickHouse из
предварительно созданного файла data.csv. Благодаря многопоточности загрузка 
занимает секунды, а не минуты.


```commandline
Upload chunk_size=100000 rows to file in 1.1527040004730225 seconds
Insert 10000000 (num_chunks=100, chunk_size=100000) rows in 0.7183911800384521 seconds
Insert speed: 13919992.725223528 rows/sec
Total time: 1.8710951805114746 sec
```

```commandline
Upload chunk_size=10000 rows to file in 0.11923384666442871 seconds
Insert 10000000 (num_chunks=1000, chunk_size=10000) rows in 1.7900891304016113 seconds
Insert speed: 5586314.016529709 rows/sec
Total time: 1.90932297706604 sec
```

```commandline
Upload chunk_size=1000 rows to file in 0.014127016067504883 seconds
Insert 10000000 (num_chunks=10000, chunk_size=1000) rows in 14.680991888046265 seconds
Insert speed: 681152.8864165044 rows/sec
Total time: 14.69511890411377 sec
```

___


# Чтение данных из Clickhouse

1. `cd clickhouse`
2. `docker-compose up`
3. `python upload_from_file.py` - создаст файл data.csv. Это необходимо для выполнения `read.py`
4. `python read.py` - во время чтения будет сэмулирована нагрузка (вставка 10000 строк в базу данных).

```commandline
query = 
            """
        SELECT
            user_id,
            max(viewed_frame)
        FROM user_viewed_frame
        WHERE ts > '2022-12-01 00:00:00'
        GROUP by user_id
        """

I) Select all rows in 0.27950429916381836 seconds
II) Select all rows in 0.3053469657897949 seconds
III) Select all rows in 0.31049418449401855 seconds
```

Результаты остаются одинаковыми при последовательных вызовах.

___
