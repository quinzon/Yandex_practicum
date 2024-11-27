FROM postgres:16

ARG POSTGRES_SQL_DB

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-16-cron \
        postgresql-16-partman && \
    rm -rf /var/lib/apt/lists/*

RUN echo "shared_preload_libraries = 'pg_cron,pg_partman_bgw'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "cron.database_name = '${POSTGRES_SQL_DB}'" >> /usr/share/postgresql/postgresql.conf.sample
