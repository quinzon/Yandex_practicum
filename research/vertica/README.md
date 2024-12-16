# Загрузка данных в Vertica

1. `cd vertica`
2. `docker-compose up`
3. `python upload.py`

Здесь мы используем метод `COPY` для загрузки данных в Vertica из файла data.csv созданного ранее. 
Благодаря многопоточности загрузка занимает секунды, а не минуты.


```commandline
Upload chunk_size=100.000 rows to file in 1.3091487884521484 seconds
Insert 10.000.000 (num_chunks=100, chunk_size=100.000) rows in 13.03419280052185 seconds
Insert speed: 767212.8342001839 rows/sec
Total time: 14.343341588973999 sec
```

```commandline
Upload chunk_size=10000 rows to file in 0.13411498069763184 seconds
Insert 10.000.000 (num_chunks=1000, chunk_size=10.000) rows in 20.340091943740845 seconds
Insert speed: 491639.8621824937 rows/sec
Total time: 20.474206924438477 sec
```

```commandline
Upload chunk_size=1000 rows to file in 0.01602315902709961 seconds
Insert 10000000 (num_chunks=10000, chunk_size=1000) rows in 116.23338913917542 seconds
Insert speed: 86033.79867058863 rows/sec
Total time: 116.24941229820251 sec
```

___

## Review
Очевидно, что меньшее количество фрагментов ускорит загрузку данных в Vertica.


# Read data from Vertica

1. `cd vertica`
2. `docker-compose up`
3. `python upload.py` - создаст файл data.csv. Это необходимо для выполнения `read.py`
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

I) Select all rows in 12.225646018981934 seconds
II) Select all rows in 1.8166570663452148 seconds
 Я предполагаю, что Vertica создает индекс после первого запроса.
III) Select all rows in 1.55625319480896 seconds
```

